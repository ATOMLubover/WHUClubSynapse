package handler

import (
	"fmt"
	"log/slog"
	"reflect"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/grpcimpl"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/redisimpl"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/jwtutil"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"golang.org/x/crypto/bcrypt"
)

type AuthHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	RedisService   redisimpl.RedisClientService
	UserService    service.UserService
	MailvrfService grpcimpl.MailvrfClientService

	Logger *slog.Logger
}

func (h *AuthHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("POST", "/verify", "PostSendVrfEmail")
}

func (h *AuthHandler) PostLogin(ctx iris.Context) {
	var reqBody dto.LoginRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Info(fmt.Sprintf("LoginRequest 结构体字段: %+v",
			reflect.VisibleFields(reflect.TypeOf(dto.LoginRequest{}))))

		h.Logger.Info("Login请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	userDetail, ok := h.UserService.Login(reqBody.Username, reqBody.Password)
	if !ok {
		h.Logger.Info("用户名或密码错误")

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户名或密码错误")
		return
	}

	token, err := h.JwtFactory.GenToken(model.UserClaims{
		Role:   userDetail.Role,
		UserId: int(userDetail.UserId),
	})
	if err != nil {
		h.Logger.Info("生成token失败",
			"error", err, "user_id", userDetail.UserId,
		)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("token生成失败")
		return
	}

	ctx.Header("Authorization", kBearerPrefix+token)

	resLoginConfirm := dto.LoginResponse{
		UserId:     int(userDetail.UserId),
		Username:   userDetail.Username,
		Email:      userDetail.Email,
		Role:       userDetail.Role,
		AvatarUrl:  userDetail.AvatarURL,
		LastActive: userDetail.LastActive.Format("2006-01-02 15:04:05"),
	}

	ctx.JSON(resLoginConfirm)
}

func (h *AuthHandler) PostSendVrfEmail(ctx iris.Context) {
	var reqBody dto.MailvrfRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	if h.RedisService.CheckVrfcodeExisting(reqBody.Email) {
		ctx.StatusCode(iris.StatusAccepted)
		ctx.Text("验证码已发送，请勿重复申请")
		return
	}

	if err := h.MailvrfService.RequestVerify(reqBody.Email); err != nil {
		h.Logger.Info("发送验证码失败",
			"error", err, "email", reqBody.Email,
		)

		ctx.StatusCode(iris.StatusServiceUnavailable)
		ctx.Text("邮箱服务不可用")
		return
	}

	ctx.Text("邮件已发送至%s", reqBody.Email)
}

func (h *AuthHandler) PostRegister(ctx iris.Context) {
	var reqBody dto.RegisterRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	if !h.RedisService.ValidateRegVrfcode(
		reqBody.Email,
		reqBody.Vrfcode,
	) {
		ctx.StatusCode(iris.StatusUnauthorized)
		ctx.Text("验证码错误")
		return
	}

	hashedBytes, err := bcrypt.GenerateFromPassword(
		[]byte(reqBody.EncryptedPassword),
		bcrypt.DefaultCost,
	)
	if err != nil {
		h.Logger.Info("bcrypt加密密码失败",
			"error", err, "encrypted_password", reqBody.EncryptedPassword,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("密码无效")
		return
	}

	newUser, err := h.UserService.Register(
		reqBody.Username,
		reqBody.Email,
		string(hashedBytes),
	)
	if err != nil {
		h.Logger.Info("用户注册失败",
			"error", err, "reqBody", reqBody,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("注册失败，请检查用户名或邮箱")
		return
	}

	resRegConfirm := dto.RegisterResponse{
		UserId:   newUser.UserId,
		Username: newUser.Username,
	}

	ctx.JSON(resRegConfirm)
}

package handler

import (
	"fmt"
	"log/slog"
	"reflect"
	"strings"
	"time"
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

type UserHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	RedisService   redisimpl.RedisClientService
	UserService    service.UserService
	MailvrfService grpcimpl.MailvrfClientService

	Logger *slog.Logger
}

func (h *UserHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/{id:int}", "GetUserInfo")
	b.Handle("GET", "/userlist", "GetUserList")

	b.Handle("POST", "/verify", "PostSendVrfEmail")
}

func (h *UserHandler) PostLogin(ctx iris.Context) {
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

func (h *UserHandler) PostSendVrfEmail(ctx iris.Context) {
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

func (h *UserHandler) PostRegister(ctx iris.Context) {
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

func (h *UserHandler) GetUserInfo(ctx iris.Context, id int) {
	if id <= 0 {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID无效")
		return
	}

	user, err := h.UserService.GetUserById(id)
	if err != nil {
		h.Logger.Info(
			"GetUserInfo失败",
			"error", err, "id", id,
		)

		ctx.StatusCode(iris.StatusNotFound)
		ctx.Text("用户ID无效")
		return
	}

	resUserInfo := dto.UserInfo{
		UserId:     user.UserId,
		Email:      user.Email,
		Role:       user.Role,
		Username:   user.Username,
		LastActive: user.LastActive.Format(time.DateTime),
	}

	ctx.JSON(resUserInfo)
}

func (h *UserHandler) GetUserList(ctx iris.Context) {
	authHeader := ctx.GetHeader("Authorization")
	if authHeader == "" {
		ctx.StatusCode(iris.StatusUnauthorized)
		return
	}

	claims := strings.TrimPrefix(authHeader, kBearerPrefix)
	userClaims, err := h.JwtFactory.ParseToken(claims)
	if err != nil {
		h.Logger.Info("claims反序列化错误",
			"error", err, "authHeader", authHeader,
		)

		ctx.StatusCode(iris.StatusUnauthorized)
		return
	}

	if userClaims.Role != "admin" {
		ctx.StatusCode(iris.StatusForbidden)
		return
	}

	offset, err := ctx.URLParamInt("offset")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("offset参数错误")
		return
	}

	num, err := ctx.URLParamInt("num")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("num参数错误")
		return
	}

	userList, err := h.UserService.GetUserList(offset, num)
	if err != nil {
		h.Logger.Info("获取用户列表失败",
			"error", err, "offset", offset, "num", num,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定范围的用户列表")
		return
	}

	resUserList := make([]dto.UserInfo, len(userList))
	for _, userModel := range userList {
		resUserList = append(resUserList, dto.UserInfo{
			UserId:     userModel.UserId,
			Email:      userModel.Email,
			LastActive: userModel.LastActive.Format(time.DateTime),
			Role:       userModel.Role,
			Username:   userModel.Username,
		})
	}

	ctx.JSON(resUserList)
}

func (h *UserHandler) GetPing(ctx iris.Context) {
	authHeader := ctx.GetHeader("Authorization")
	if authHeader == "" {
		ctx.StatusCode(iris.StatusUnauthorized)
		return
	}

	claims := strings.TrimPrefix(authHeader, kBearerPrefix)
	userClaims, err := h.JwtFactory.ParseToken(claims)
	if err != nil {
		h.Logger.Info("claims反序列化错误",
			"error", err, "authHeader", authHeader,
		)

		ctx.StatusCode(iris.StatusUnauthorized)
		return
	}

	if err := h.UserService.KeepUserActive(userClaims.UserId, userClaims.Role); err != nil {
		h.Logger.Info("更新用户状态失败",
			"error", err, "user_id", userClaims.UserId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("更新用户状态失败")
		return
	}

	ctx.Text("pong")
}

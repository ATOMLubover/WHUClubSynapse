package handler

import (
	"log/slog"
	"time"
	"whuclubsynapse-server/internal/auth_server/dto"
	"whuclubsynapse-server/internal/auth_server/grpcimpl"
	"whuclubsynapse-server/internal/auth_server/redisimpl"
	"whuclubsynapse-server/internal/auth_server/service"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"golang.org/x/crypto/bcrypt"
)

type UserHandler struct {
	CtxIris iris.Context

	RedisService redisimpl.RedisClientService

	UserService    service.UserService
	MailvrfService grpcimpl.MailvrfClientService

	Logger *slog.Logger
}

func (h *UserHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/{id:int}", "GetUserInfo")
	b.Handle("POST", "/verify", "PostSendVrfEmail")
	b.Handle("PUT", "/ping", "PutPong")
}

func (h *UserHandler) PostLogin() {
	var reqBody dto.LoginRequest
	if err := h.CtxIris.ReadJSON(&reqBody); err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	hashedBytes, err := bcrypt.GenerateFromPassword(
		[]byte(reqBody.EncryptedPassword),
		bcrypt.DefaultCost,
	)
	if err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	userModel, ok := h.UserService.Login(reqBody.Username, string(hashedBytes))
	if !ok {
		h.CtxIris.StopWithText(
			iris.StatusUnauthorized,
			"用户名或密码错误",
		)
		return
	}

	resBody := dto.LoginResponse{
		Id:         int(userModel.UserId),
		Username:   userModel.Username,
		Email:      userModel.Email,
		Role:       userModel.Role,
		AvatarUrl:  userModel.AvatarURL,
		LastActive: userModel.LastActive.Format("2006-01-02 15:04:05"),
	}
	h.CtxIris.JSON(resBody)
}

func (h *UserHandler) PostSendVrfEmail() {
	var reqBody dto.MailvrfRequest
	if err := h.CtxIris.ReadJSON(&reqBody); err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	if err := h.MailvrfService.RequestVerify(reqBody.Email); err != nil {
		h.CtxIris.StopWithText(
			iris.StatusServiceUnavailable,
			"邮箱验证服务不可用",
		)
		return
	}

	h.CtxIris.Text("邮件已发送至%s", reqBody.Email)
}

func (h *UserHandler) PostRegister() {
	var reqBody dto.RegisterRequest
	if err := h.CtxIris.ReadJSON(&reqBody); err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	if !h.RedisService.ValidateRegVrfcode(
		reqBody.Email,
		reqBody.Vrfcode,
	) {
		h.CtxIris.StopWithText(
			iris.StatusForbidden,
			"邮箱验证码错误",
		)
		return
	}

	hashedBytes, err := bcrypt.GenerateFromPassword(
		[]byte(reqBody.EncryptedPassword),
		bcrypt.DefaultCost,
	)
	if err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	newUser, err := h.UserService.Register(
		reqBody.Username,
		reqBody.Email,
		string(hashedBytes),
	)
	if err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	resBody := dto.RegisterResponse{
		Id:       newUser.UserId,
		Username: newUser.Username,
	}

	h.CtxIris.JSON(resBody)
}

func (h *UserHandler) GetUserInfo(id int) {
	if id <= 0 {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	user, err := h.UserService.GetUserById(uint(id))
	if err != nil {
		h.CtxIris.StopWithStatus(iris.StatusNotFound)
		return
	}

	userInfo := dto.UserInfo{
		Id:         user.UserId,
		Email:      user.Email,
		LastActive: user.LastActive.Format(time.DateTime),
		Role:       user.Role,
		Username:   user.Username,
	}
	h.CtxIris.JSON(userInfo)
}

func (h *UserHandler) GetUserList() {
	offset, err := h.CtxIris.URLParamInt("offset")
	if err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	num, err := h.CtxIris.URLParamInt("num")
	if err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	userList, err := h.UserService.GetUserList(offset, num)
	if err != nil {
		h.CtxIris.StopWithStatus(iris.StatusBadRequest)
		return
	}

	userListDto := make([]dto.UserInfo, len(userList))
	for _, userModel := range userList {
		userListDto = append(userListDto, dto.UserInfo{
			Id:         userModel.UserId,
			Email:      userModel.Email,
			LastActive: userModel.LastActive.Format(time.DateTime),
			Role:       userModel.Role,
			Username:   userModel.Username,
		})
	}

	h.CtxIris.JSON(userListDto)
}

func (h *UserHandler) PutPong() {
	h.CtxIris.Text("pong")
}

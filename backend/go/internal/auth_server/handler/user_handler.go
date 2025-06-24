package handler

import (
	"log/slog"
	"whuclubsynapse-server/internal/auth_server/dto"
	"whuclubsynapse-server/internal/auth_server/model"
	"whuclubsynapse-server/internal/auth_server/service"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"golang.org/x/crypto/bcrypt"
)

type UserHandler struct {
	Context iris.Context

	UserService service.UserService
	Logger      *slog.Logger
}

func (h *UserHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/{id:int}", "GetUserInfo")
	b.Handle("PUT", "/ping", "PutPong")
}

func (h *UserHandler) PostLogin() mvc.Result {
	var reqBody dto.LoginRequest
	if err := h.Context.ReadJSON(&reqBody); err != nil {
		return mvc.Response{
			Code: iris.StatusBadRequest,
		}
	}

	hashedBytes, err := bcrypt.GenerateFromPassword(
		[]byte(reqBody.EncryptedPassword),
		bcrypt.DefaultCost,
	)
	if err != nil {
		return mvc.Response{
			Code: iris.StatusInternalServerError,
		}
	}

	userModel := model.User{
		Username:     reqBody.Username,
		PasswordHash: string(hashedBytes),
	}
	h.UserService.Login(userModel)

	return mvc.Response{}
}

func (h *UserHandler) PostRegister() mvc.Result {
	return mvc.Response{}
}

func (h *UserHandler) GetUserInfo(id int) mvc.Result {
	return mvc.Response{}
}

func (h *UserHandler) PutPong() mvc.Result {
	return mvc.Response{}
}

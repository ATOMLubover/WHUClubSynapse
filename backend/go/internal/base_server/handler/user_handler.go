package handler

import (
	"io"
	"log/slog"
	"mime"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/dbstruct"
	"whuclubsynapse-server/internal/shared/jwtutil"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"golang.org/x/crypto/bcrypt"
)

const (
	USR_AVATAR_DIR = "pub/user_avatars"
)

type UserHandler struct {
	JwtFactory  *jwtutil.CliamsFactory[model.UserClaims]
	UserService service.UserService

	Logger *slog.Logger
}

func (h *UserHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/{id:int}", "GetUserInfo")
	b.Handle("GET", "/list", "GetUserList")
	b.Handle("GET", "/ping", "GetPing")

	b.Handle("POST", "/upload_avatar", "PostUploadAvatar")
	b.Handle("PUT", "/update", "PutUpdateUserInfo")
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
		AvatarUrl:  user.AvatarUrl,
		Username:   user.Username,
		LastActive: user.LastActive.Format("2006-01-02 15:04:05"),
		Extension:  user.Extension,
	}

	ctx.JSON(resUserInfo)
}

func (h *UserHandler) GetUserList(ctx iris.Context) {
	userRole := ctx.Values().GetString("user_claims_user_role")
	if userRole == "" {
		ctx.StopWithStatus(iris.StatusBadRequest)
		return
	}

	if userRole != dbstruct.ROLE_ADMIN {
		ctx.StopWithStatus(iris.StatusForbidden)
		return
	}

	offset := ctx.URLParamIntDefault("offset", 0)
	num := ctx.URLParamIntDefault("num", 10)

	userList, err := h.UserService.GetUserList(offset, num)
	if err != nil {
		h.Logger.Info("获取用户列表失败",
			"error", err, "offset", offset, "num", num,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定范围的用户列表")
		return
	}

	var resUserList []dto.UserInfo
	for _, userModel := range userList {
		resUserList = append(resUserList, dto.UserInfo{
			UserId:     userModel.UserId,
			Email:      userModel.Email,
			LastActive: userModel.LastActive.Format("2006-01-02 15:04:05"),
			AvatarUrl:  userModel.AvatarUrl,
			Role:       userModel.Role,
			Username:   userModel.Username,
			Extension:  userModel.Extension,

			CreatedAt: userModel.CreatedAt.Format("2006-01-02 15:04:05"),
			UpdatedAt: userModel.UpdatedAt.Format("2006-01-02 15:04:05"),
		})
	}

	ctx.JSON(resUserList)
}

func (h *UserHandler) GetPing(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		return
	}

	userRole := ctx.Values().GetString("user_claims_user_role")
	if userRole == "" {
		ctx.StatusCode(iris.StatusForbidden)
		return
	}

	if err := h.UserService.KeepUserActive(userId, userRole); err != nil {
		h.Logger.Info("更新用户状态失败",
			"error", err, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("更新用户状态失败")
		return
	}

	ctx.Text("pong")
}

func (h *UserHandler) PostUploadAvatar(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		return
	}

	file, header, err := ctx.FormFile("avatar")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("未成功获取上传的logo文件")
		return
	}

	defer file.Close()

	var detectedContentType string

	if clientContentType := header.Header.Get("Content-Type"); clientContentType != "" {
		detectedContentType = clientContentType
	} else {
		fileHeaderBytes := make([]byte, 512)
		_, readErr := file.Read(fileHeaderBytes)
		if readErr != nil && readErr != io.EOF {
			ctx.StatusCode(iris.StatusBadRequest)
			ctx.Text("无法读取文件头部以检测类型。")
			return
		}

		_, seekErr := file.Seek(0, 0)
		if seekErr != nil {
			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法重置文件读取位置。")
			return
		}

		detectedContentType = http.DetectContentType(fileHeaderBytes)
	}

	var fileExtension string

	extensions, err := mime.ExtensionsByType(detectedContentType)
	if err == nil && len(extensions) > 0 {
		fileExtension = extensions[0]
		if !strings.HasPrefix(fileExtension, ".") {
			fileExtension = "." + fileExtension
		}
	} else {
		fileExtension = ".bin"
	}

	if err := os.MkdirAll(USR_AVATAR_DIR, os.ModePerm); err != nil {
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("目录创建失败")
		return
	}

	filePath := filepath.Join(USR_AVATAR_DIR, "avatar_"+strconv.Itoa(userId)+fileExtension)
	dst, err := os.Create(filePath)
	if err != nil {
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("文件创建失败")
		return
	}
	defer dst.Close()

	if _, err := io.Copy(dst, file); err != nil {
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("文件保存失败")
		return
	}

	if err := h.UserService.UpdateAvatar(userId, filePath); err != nil {
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("数据库更新失败")
		return
	}

	ctx.JSON(iris.Map{"status": "文件上传成功", "path": filePath})
}

func (h *UserHandler) PutUpdateUserInfo(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID获取失败")
		return
	}

	var reqBody dto.UpdateUserRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Info("UpdateUser请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	hashedBytes, err := bcrypt.GenerateFromPassword(
		[]byte(reqBody.Password),
		bcrypt.DefaultCost,
	)
	if err != nil {
		h.Logger.Info("bcrypt加密密码失败",
			"error", err, "encrypted_password", reqBody.Password,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("密码无效")
		return
	}

	if err := h.UserService.UpdateUser(&dbstruct.User{
		UserId:       uint(userId),
		Username:     reqBody.Username,
		PasswordHash: string(hashedBytes),
		Email:        reqBody.Email,
		Extension:    reqBody.Extension,
	}); err != nil {
		h.Logger.Info("更新用户信息失败",
			"error", err, "user_id", reqBody.UserId,
		)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("更新用户信息失败")
		return
	}

	ctx.Text("更新用户信息成功")
}

package repo

import (
	"errors"
	"fmt"
	"log/slog"
	"whuclubsynapse-server/internal/auth_server/model"

	"gorm.io/gorm"
)

type UserRepo interface {
	CreateUser(user *model.User) error
	GetUserById(id uint) (*model.User, error)
	GetUserByUsername(username string) (*model.User, error)
	GetUserList(offset int, num int) ([]*model.User, error)
}

func CreateUserRepo(
	database *gorm.DB,
	logger *slog.Logger,
) UserRepo {
	return &sUserRepo{
		database: database,
		logger:   logger,
	}
}

type sUserRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func (r *sUserRepo) CreateUser(user *model.User) error {
	if user == nil {
		return errors.New("CreateUser失败：user为空")
	}

	result := r.database.Create(user)
	if result.Error != nil {
		r.logger.Error(
			"CreateUser数据库操作异常",
			"error", result.Error,
			"username", user.Username,
		)
		return result.Error
	}

	if result.RowsAffected == 0 {
		r.logger.Warn("CreateUser影响行为0",
			"username", user.Username,
		)
		return fmt.Errorf("CreateUser失败：影响行为为0")
	}

	r.logger.Debug(
		"用户创建成功",
		"userId", user.UserId,
		"username", user.Username,
	)

	return nil
}

func (r *sUserRepo) GetUserById(id uint) (*model.User, error) {
	if id <= 0 {
		return nil, errors.New("无效用户ID")
	}

	var userModel model.User

	result := r.database.First(&userModel, id)
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return nil, fmt.Errorf("未找到用户ID：%d", id)
	}
	if result.Error != nil {
		r.logger.Error(
			"GetUserById数据库操作异常",
			"error", result.Error,
			"id", id,
		)
		return nil, result.Error
	}

	return &userModel, nil
}

func (r *sUserRepo) GetUserByUsername(username string) (*model.User, error) {
	if username == "" {
		return nil, errors.New("无效用户名")
	}

	var user model.User

	result := r.database.Where("username = ?", username).First(&user)
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return nil, fmt.Errorf("用户不存在：%s", username)
	}
	if result.Error != nil {
		r.logger.Error("GetUserByUsername数据库操作异常",
			"error", result.Error,
			"username", username,
		)
		return nil, result.Error
	}

	return &user, nil
}

func (r *sUserRepo) GetUserList(offset int, num int) ([]*model.User, error) {
	var users []*model.User

	result := r.database.Where("user_id > ?", offset).
		Limit(num).Find(&users)
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		r.logger.Info("数据库为空")
		return []*model.User{}, nil
	}
	if result.Error != nil {
		r.logger.Error("GetUserList数据库操作异常", "error", result.Error)
		return nil, result.Error
	}

	r.logger.Debug("已提取用户列表", "长度", len(users))
	return users, nil
}

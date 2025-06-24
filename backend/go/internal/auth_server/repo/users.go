package repo

import (
	"log/slog"
	"whuclubsynapse-server/internal/auth_server/model"

	"gorm.io/gorm"
)

type UserRepo interface {
	CreateUser(user *model.User) error
	GetUserById(id int) (*model.User, error)
	GetUserByUsername(username string) (*model.User, error)
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
	r.logger.Debug("Create User", "user", *user)
	return nil
}

func (r *sUserRepo) GetUserById(id int) (*model.User, error) {
	r.logger.Debug("Get user", "id", id)
	return &model.User{}, nil
}

func (r *sUserRepo) GetUserByUsername(username string) (*model.User, error) {
	r.logger.Debug("Get user", "username", username)
	return &model.User{}, nil
}

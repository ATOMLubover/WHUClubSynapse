package repo

import (
	"errors"
	"log/slog"
	"time"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type UserRepo interface {
	AddUser(user *dbstruct.User) error
	GetUserById(id int) (*dbstruct.User, error)
	GetUserByUsername(username string) (*dbstruct.User, error)
	GetUserList(offset int, num int) ([]*dbstruct.User, error)
	UpdateUserLastActive(id int) error
	UpdateUserRole(tx *gorm.DB, id int, role string) error
}

type sUserRepo struct {
	database *gorm.DB
	logger   *slog.Logger
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

func (r *sUserRepo) AddUser(user *dbstruct.User) error {
	return r.database.Create(user).Error
}

func (r *sUserRepo) GetUserById(id int) (*dbstruct.User, error) {
	if id <= 0 {
		return nil, errors.New("无效用户ID")
	}

	var userModel dbstruct.User
	err := r.database.First(&userModel, id).Error

	return &userModel, err
}

func (r *sUserRepo) GetUserByUsername(username string) (*dbstruct.User, error) {
	if username == "" {
		return nil, errors.New("无效用户名")
	}

	var user dbstruct.User
	err := r.database.
		Where("username = ?", username).
		First(&user).Error

	return &user, err
}

func (r *sUserRepo) GetUserList(offset int, num int) ([]*dbstruct.User, error) {
	if offset < 0 || num <= 0 {
		return nil, errors.New("无效参数")
	}

	var users []*dbstruct.User
	err := r.database.
		Model(&dbstruct.User{}).
		Offset(offset).
		Limit(num).
		Find(&users).Error

	return users, err
}

func (r *sUserRepo) UpdateUserLastActive(id int) error {
	return r.database.
		Model(&dbstruct.User{}).
		Where("user_id = ?", id).
		Update("last_active", time.Now()).Error
}

func (r *sUserRepo) UpdateUserRole(tx *gorm.DB, id int, role string) error {
	return r.database.
		Model(&dbstruct.User{}).
		Where("user_id = ? AND role = 'user'", id).
		Update("role", role).Error
}

package service

import (
	"whuclubsynapse-server/internal/auth_server/model"
	"whuclubsynapse-server/internal/auth_server/repo"
)

type UserService interface {
	Login(user model.User) bool
	Register(user model.User) (*model.User, error)
	GetUserById(id int) (*model.User, error)
}

func NewUserService(
	repo repo.UserRepo,
) UserService {
	return &sUserService{
		Repo: repo,
	}
}

type sUserService struct {
	Repo repo.UserRepo
}

func (s *sUserService) Login(user model.User) bool {
	userModel, err := s.Repo.GetUserByUsername(user.Username)
	if err != nil {
		return false
	}

	if userModel.PasswordHash != user.PasswordHash {
		return false
	}

	return true
}

func (s *sUserService) Register(user model.User) (*model.User, error) {
	if err := s.Repo.CreateUser(&user); err != nil {
		return nil, err
	}
	userModel, err := s.Repo.GetUserByUsername(user.Username)
	if err != nil {
		return nil, err
	}

	return userModel, nil
}

func (s *sUserService) GetUserById(id int) (*model.User, error) {
	userModel, err := s.Repo.GetUserById(id)
	if err != nil {
		return nil, err
	}

	return userModel, nil
}

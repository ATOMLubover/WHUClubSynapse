package service

import (
	"whuclubsynapse-server/internal/auth_server/model"
	"whuclubsynapse-server/internal/auth_server/repo"
)

type UserService interface {
	Login(username, passwordHash string) (*model.User, bool)
	Register(username, email, passwordHash string) (*model.User, error)
	GetUserById(id uint) (*model.User, error)
	GetUserList(offset int, num int) ([]*model.User, error)
}

type sUserService struct {
	UserRepo repo.UserRepo
}

func NewUserService(
	userRepo repo.UserRepo,
) UserService {
	return &sUserService{
		UserRepo: userRepo,
	}
}

func (s *sUserService) Login(username, passwordHash string) (*model.User, bool) {
	userModel, err := s.UserRepo.GetUserByUsername(username)
	if err != nil {
		return nil, false
	}

	if userModel.PasswordHash != passwordHash {
		return nil, false
	}

	return userModel, true
}

func (s *sUserService) Register(username, email, passwordHash string) (*model.User, error) {
	newUser := model.User{
		Username:     username,
		Email:        email,
		PasswordHash: passwordHash,
	}

	if err := s.UserRepo.CreateUser(&newUser); err != nil {
		return nil, err
	}

	userModel, err := s.UserRepo.GetUserByUsername(username)
	if err != nil {
		return nil, err
	}

	return userModel, nil
}

func (s *sUserService) GetUserById(id uint) (*model.User, error) {
	userModel, err := s.UserRepo.GetUserById(id)
	if err != nil {
		return nil, err
	}

	return userModel, nil
}

func (s *sUserService) GetUserList(offset int, num int) ([]*model.User, error) {
	userModelList, err := s.UserRepo.GetUserList(offset, num)
	if err != nil {
		return nil, err
	}

	return userModelList, nil
}

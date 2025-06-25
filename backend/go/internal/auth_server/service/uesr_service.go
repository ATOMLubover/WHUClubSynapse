package service

import (
	"errors"
	"whuclubsynapse-server/internal/auth_server/model"
	"whuclubsynapse-server/internal/auth_server/repo"

	"golang.org/x/crypto/bcrypt"
)

type UserService interface {
	Login(username, rawPassword string) (*model.User, bool)
	Register(username, email, passwordHash string) (*model.User, error)
	GetUserById(id uint) (*model.User, error)
	GetUserList(offset int, num int) ([]*model.User, error)
	KeepUserActive(id uint, role string) error
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

func (s *sUserService) Login(username, rawPassword string) (*model.User, bool) {
	userModel, err := s.UserRepo.GetUserByUsername(username)
	if err != nil {
		return nil, false
	}

	if err := bcrypt.CompareHashAndPassword(
		[]byte(userModel.PasswordHash),
		[]byte(rawPassword),
	); err != nil {
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

func (s *sUserService) KeepUserActive(id uint, role string) error {
	userModel, err := s.UserRepo.GetUserById(id)
	if err != nil {
		return err
	}

	if userModel.Role != role {
		return errors.New("用户身份错误")
	}

	err = s.UserRepo.UpdateUserLastActive(id)
	if err != nil {
		return err
	}

	return nil
}

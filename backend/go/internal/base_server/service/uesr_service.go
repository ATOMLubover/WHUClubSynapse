package service

import (
	"errors"
	"whuclubsynapse-server/internal/base_server/repo"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"golang.org/x/crypto/bcrypt"
)

type UserService interface {
	Login(username, rawPassword string) (*dbstruct.User, bool)
	Register(username, email, passwordHash string) (*dbstruct.User, error)
	GetUserById(id int) (*dbstruct.User, error)
	GetUserList(offset int, num int) ([]*dbstruct.User, error)
	KeepUserActive(id int, role string) error
	UpdateAvatar(id int, avatarUrl string) error
	UpdateUser(newUser *dbstruct.User) error
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

func (s *sUserService) Login(username, rawPassword string) (*dbstruct.User, bool) {
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

func (s *sUserService) Register(username, email, passwordHash string) (*dbstruct.User, error) {
	newUser := dbstruct.User{
		Username:     username,
		Email:        email,
		PasswordHash: passwordHash,
	}

	if err := s.UserRepo.AddUser(&newUser); err != nil {
		return nil, err
	}

	return &newUser, nil
}

func (s *sUserService) GetUserById(id int) (*dbstruct.User, error) {
	userModel, err := s.UserRepo.GetUserById(id)
	if err != nil {
		return nil, err
	}

	return userModel, nil
}

func (s *sUserService) GetUserList(offset int, num int) ([]*dbstruct.User, error) {
	userModelList, err := s.UserRepo.GetUserList(offset, num)
	if err != nil {
		return nil, err
	}

	return userModelList, nil
}

func (s *sUserService) KeepUserActive(id int, role string) error {
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

func (s *sUserService) UpdateAvatar(id int, avatarUrl string) error {
	return s.UserRepo.UpdateAvatar(id, avatarUrl)
}

func (s *sUserService) UpdateUser(newUser *dbstruct.User) error {
	if newUser.UserId <= 0 {
		return errors.New("无效用户ID")
	}

	return s.UserRepo.UpdateUser(newUser)
}

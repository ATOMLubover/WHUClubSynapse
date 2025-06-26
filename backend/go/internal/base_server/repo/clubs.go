package repo

import (
	"errors"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type ClubRepo interface {
	AddClub(club dbstruct.Club) error
	GetClubList(offset, num int) ([]*dbstruct.Club, error)
	GetClubInfo(id int) (*dbstruct.Club, error)
	GetClubsByCategory(catId int) ([]*dbstruct.Club, error)
	GetLatestClubs() ([]*dbstruct.Club, error)
	UpdateClubInfo(newInfo dbstruct.Club) error
}

type sClubRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateClubRepo(
	database *gorm.DB,
	logger *slog.Logger,
) ClubRepo {
	return &sClubRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sClubRepo) AddClub(club dbstruct.Club) error {
	return r.database.Create(&club).Error
}

func (r *sClubRepo) GetClubList(offset, num int) ([]*dbstruct.Club, error) {
	var clubs []*dbstruct.Club
	err := r.database.
		Offset(offset).
		Limit(num).
		Find(&clubs).Error
	return clubs, err
}

func (r *sClubRepo) GetClubInfo(id int) (*dbstruct.Club, error) {
	if id <= 0 {
		return nil, errors.New("无效的社团ID")
	}

	var club dbstruct.Club
	err := r.database.
		Where("club_id = ?", id).
		First(&club).Error

	return &club, err
}

func (r *sClubRepo) GetClubsByCategory(catId int) ([]*dbstruct.Club, error) {
	if catId <= 0 {
		return nil, errors.New("无效的分类ID")
	}

	var clubs []*dbstruct.Club
	err := r.database.
		Where("category_id = ?", catId).
		Limit(20).
		Find(&clubs).Error

	return clubs, err
}

func (r *sClubRepo) GetLatestClubs() ([]*dbstruct.Club, error) {
	var clubs []*dbstruct.Club
	err := r.database.
		Order("created_at DESC").
		Limit(5).
		Find(&clubs).Error
	return clubs, err
}

func (r *sClubRepo) UpdateClubInfo(newInfo dbstruct.Club) error {
	return r.database.
		Where("club_id = ?", newInfo.ClubId).
		Updates(newInfo).Error
}

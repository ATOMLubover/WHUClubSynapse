package repo

import (
	"errors"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type ClubRepo interface {
	AddClub(club *dbstruct.Club) error
	AppendClub(tx *gorm.DB, club *dbstruct.Club) error
	GetClubList(offset, num int) ([]*dbstruct.Club, error)
	GetClubInfo(id int) (*dbstruct.Club, error)
	GetClubsByCategory(catId int) ([]*dbstruct.Club, error)
	GetLatestClubs() ([]*dbstruct.Club, error)
	GetClubNum() (int64, error)
	UpdateClubInfo(tx *gorm.DB, newInfo dbstruct.Club) error
	UpdateClubLogo(clubId int, logoUrl string) error

	DeleteClub(tx *gorm.DB, clubId int) error
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

func (r *sClubRepo) AddClub(club *dbstruct.Club) error {
	return r.database.Create(club).Error
}

func (r *sClubRepo) AppendClub(tx *gorm.DB, club *dbstruct.Club) error {
	return tx.Create(club).Error
}

func (r *sClubRepo) GetClubList(offset, num int) ([]*dbstruct.Club, error) {
	var clubs []*dbstruct.Club
	err := r.database.
		Order("created_at DESC").
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
		Model(&dbstruct.Club{}).
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

func (r *sClubRepo) GetClubNum() (int64, error) {
	var count int64
	err := r.database.
		Model(&dbstruct.Club{}).
		Select("club_id").
		Count(&count).Error
	return count, err
}

func (r *sClubRepo) UpdateClubInfo(tx *gorm.DB, newInfo dbstruct.Club) error {
	return tx.
		Where("club_id = ?", newInfo.ClubId).
		Updates(newInfo).Error
}

func (r *sClubRepo) UpdateClubLogo(clubId int, logoUrl string) error {
	return r.database.
		Model(&dbstruct.Club{}).
		Where("club_id = ?", clubId).
		Update("logo_url", logoUrl).Error
}

func (r *sClubRepo) DeleteClub(tx *gorm.DB, clubId int) error {
	if err := tx.
		Model(&dbstruct.Club{}).
		Where("club_id = ?", clubId).
		Delete(&dbstruct.Club{}).Error; err != nil {
		r.logger.Error("删除社团失败", "club_id", clubId, "error", err)
		return err
	}

	return nil
}

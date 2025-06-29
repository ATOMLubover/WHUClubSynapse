package repo

import (
	"errors"
	"log/slog"
	"time"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type ClubFavouriteRepo interface {
	AddClubFavourite(userId, clubId int) error
	RemoveClubFavourite(userId, clubId int) error

	GetClubFavorites(userId int) ([]uint, error)
}

type sClubFavouriteRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateClubFavoriteRepo(database *gorm.DB, logger *slog.Logger) ClubFavouriteRepo {
	return &sClubFavouriteRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sClubFavouriteRepo) AddClubFavourite(userId, clubId int) error {
	var fav dbstruct.ClubFavorite
	err := r.database.
		Where("user_id = ? AND club_id = ?",
			userId, clubId).
		First(&fav).Error
	switch {
	case errors.Is(err, gorm.ErrRecordNotFound):
		return r.database.Create(&dbstruct.ClubFavorite{
			UserId:    uint(userId),
			ClubId:    uint(clubId),
			CreatedAt: time.Now(),
			DeletedAt: time.Time{},
		}).Error

	default:
		return err
	}
}

func (r *sClubFavouriteRepo) RemoveClubFavourite(userId, clubId int) error {
	return r.database.
		Model(&dbstruct.ClubFavorite{}).
		Where("user_id = ? AND club_id = ?", userId, clubId).
		Update("deleted_at", time.Now()).Error
}

func (r *sClubFavouriteRepo) GetClubFavorites(userId int) ([]uint, error) {
	var clubSerials []uint
	err := r.database.
		Model(&dbstruct.ClubFavorite{}).
		Where("user_id = ?", userId).
		Pluck("club_id", &clubSerials).Error
	return clubSerials, err
}

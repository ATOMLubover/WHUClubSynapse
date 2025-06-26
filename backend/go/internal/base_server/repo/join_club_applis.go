package repo

import (
	"errors"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type JoinClubAppliRepo interface {
	AddJoinClubAppli(appli dbstruct.JoinClubApplication) error
	GetJoinClubAppliList(clubId int) ([]*dbstruct.JoinClubApplication, error)
	ApproveAppli(appliId int) error
	RejectAppli(appliId int, reason string) error
}

type sJoinClubAppliRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateJoinClubAppliRepo(
	database *gorm.DB,
	logger *slog.Logger,
) JoinClubAppliRepo {
	return &sJoinClubAppliRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sJoinClubAppliRepo) AddJoinClubAppli(appli dbstruct.JoinClubApplication) error {
	return r.database.Create(&appli).Error
}

func (r *sJoinClubAppliRepo) GetJoinClubAppliList(clubId int) ([]*dbstruct.JoinClubApplication, error) {
	if clubId <= 0 {
		return nil, errors.New("无效参数")
	}

	var appliList []*dbstruct.JoinClubApplication
	err := r.database.
		Model(&dbstruct.JoinClubApplication{}).
		Where("club_id = ?", clubId).
		Find(&appliList).Error

	return appliList, err
}

func (r *sJoinClubAppliRepo) ApproveAppli(appliId int) error {
	if appliId <= 0 {
		return errors.New("无效参数")
	}

	return r.database.
		Model(&dbstruct.JoinClubApplication{}).
		Where("join_appli_id = ?", appliId).
		Update("status", "approved").Error
}

func (r *sJoinClubAppliRepo) RejectAppli(appliId int, reason string) error {
	return r.database.
		Model(&dbstruct.JoinClubApplication{}).
		Where("join_appli_id = ?", appliId).
		Select("status", "reason").
		Updates(dbstruct.JoinClubApplication{
			Status:         "rejected",
			RejectedReason: reason,
		}).Error
}

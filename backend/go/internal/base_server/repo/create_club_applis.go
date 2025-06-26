package repo

import (
	"errors"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type CreateClubAppliRepo interface {
	AddCreateClubAppli(appli dbstruct.CreateClubApplication) error
	GetCreateClubAppliList(offset, num int) ([]*dbstruct.CreateClubApplication, error)
	ApproveAppli(appliId int) error
	RejectAppli(appliId int, reason string) error
}

type sCreateClubAppliRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func (r *sCreateClubAppliRepo) AddCreateClubAppli(appli dbstruct.CreateClubApplication) error {
	return r.database.Create(&appli).Error
}

func (r *sCreateClubAppliRepo) GetCreateClubAppliList(offset, num int) ([]*dbstruct.CreateClubApplication, error) {
	if num <= 0 || offset < 0 {
		return nil, errors.New("无效参数")
	}

	var list []*dbstruct.CreateClubApplication
	err := r.database.
		Limit(num).
		Offset(offset).
		Find(&list).Error
	return list, err
}

func (r *sCreateClubAppliRepo) ApproveAppli(appliId int) error {
	if appliId <= 0 {
		return errors.New("无效参数")
	}

	return r.database.
		Model(&dbstruct.CreateClubApplication{}).
		Where("create_appli_id = ?", appliId).
		Update("status", "approved").Error
}

func (r *sCreateClubAppliRepo) RejectAppli(appliId int, reason string) error {
	if appliId <= 0 {
		return errors.New("无效参数")
	}

	return r.database.
		Model(&dbstruct.CreateClubApplication{}).
		Where("create_appli_id = ?", appliId).
		Select("status", "reason").
		Updates(dbstruct.CreateClubApplication{
			Status:         "rejected",
			RejectedReason: reason,
		}).Error
}

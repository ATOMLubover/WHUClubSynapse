package repo

import (
	"errors"
	"fmt"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type CreateClubAppliRepo interface {
	AddCreateClubAppli(appli *dbstruct.CreateClubAppli) error
	GetCreateClubAppliList(userId int) ([]*dbstruct.CreateClubAppli, error)
	GetApplisByUserId(userId int) ([]*dbstruct.CreateClubAppli, error)
	GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.CreateClubAppli, error)
	ApproveAppli(tx *gorm.DB, appliId int) error
	RejectAppli(appliId int, reason string) error
}

type sCreateClubAppliRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateCreateClubAppliRepo(
	database *gorm.DB,
	logger *slog.Logger,
) CreateClubAppliRepo {
	return &sCreateClubAppliRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sCreateClubAppliRepo) AddCreateClubAppli(appli *dbstruct.CreateClubAppli) error {
	return r.database.Transaction(func(tx *gorm.DB) error {
		var existing dbstruct.CreateClubAppli
		err := tx.
			//Clauses(clause.Locking{Strength: "UPDATE"}).
			Where("user_id = ? AND status = 'pending'", appli.UserId).
			First(&existing).Error

		if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
			return err
		}

		if existing.CreateAppliId != 0 {
			return fmt.Errorf("用户（user_id: %d） 有正在处理的申请", appli.UserId)
		}

		return tx.Create(appli).Error
	})
}

func (r *sCreateClubAppliRepo) GetCreateClubAppliList(clubId int) ([]*dbstruct.CreateClubAppli, error) {
	var list []*dbstruct.CreateClubAppli
	err := r.database.
		Model(&dbstruct.CreateClubAppli{}).
		Where("user_id = ?", clubId).
		Find(&list).Error
	return list, err
}

func (r *sCreateClubAppliRepo) GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.CreateClubAppli, error) {
	if appliId <= 0 {
		return nil, errors.New("无效参数")
	}

	var appli dbstruct.CreateClubAppli
	err := tx.
		//Clauses(clause.Locking{Strength: "UPDATE"}).
		Where("create_appli_id = ?", appliId).
		First(&appli).Error

	return &appli, err
}

func (r *sCreateClubAppliRepo) GetApplisByUserId(userId int) ([]*dbstruct.CreateClubAppli, error) {
	var list []*dbstruct.CreateClubAppli
	err := r.database.
		Where("user_id = ?", userId).
		Find(&list).Error
	return list, err
}

func (r *sCreateClubAppliRepo) ApproveAppli(tx *gorm.DB, appliId int) error {
	if appliId <= 0 {
		return errors.New("无效参数")
	}

	return r.database.
		Model(&dbstruct.CreateClubAppli{}).
		Where("create_appli_id = ?", appliId).
		Update("status", "approved").Error
}

func (r *sCreateClubAppliRepo) RejectAppli(appliId int, reason string) error {
	if appliId <= 0 {
		return errors.New("无效参数")
	}

	return r.database.
		Model(&dbstruct.CreateClubAppli{}).
		Where("create_appli_id = ?", appliId).
		Select("status", "reason").
		Updates(dbstruct.CreateClubAppli{
			Status:         "rejected",
			RejectedReason: reason,
		}).Error
}

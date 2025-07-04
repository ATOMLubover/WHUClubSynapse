package repo

import (
	"errors"
	"fmt"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type UpdateClubInfoAppliRepo interface {
	AddUpdateClubInfoAppli(appli *dbstruct.UpdateClubInfoAppli) error
	GetUpdateList(offset, num int) ([]*dbstruct.UpdateClubInfoAppli, error)
	GetApplisByUserId(userId int) ([]*dbstruct.UpdateClubInfoAppli, error)
	GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.UpdateClubInfoAppli, error)
	ApproveAppli(tx *gorm.DB, appliId int) error
	RejectAppli(appliId int, reason string) error
}

type sUpdateClubInfoAppliRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateUpdateClubInfoAppliRepo(
	database *gorm.DB,
	logger *slog.Logger,
) UpdateClubInfoAppliRepo {
	return &sUpdateClubInfoAppliRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sUpdateClubInfoAppliRepo) AddUpdateClubInfoAppli(appli *dbstruct.UpdateClubInfoAppli) error {
	return r.database.Transaction(func(tx *gorm.DB) error {
		var existing dbstruct.UpdateClubInfoAppli
		err := tx.
			//Clauses(clause.Locking{Strength: "UPDATE"}).
			Where("club_id = ? AND status = 'pending'", appli.ClubId).
			First(&existing).Error

		if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
			return err
		}

		if existing.UpdateAppliId != 0 {
			return fmt.Errorf("社团（club_id: %d） 有正在处理的更新申请", appli.ClubId)
		}

		return tx.Create(appli).Error
	})
}

func (r *sUpdateClubInfoAppliRepo) GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.UpdateClubInfoAppli, error) {
	var appli dbstruct.UpdateClubInfoAppli
	err := tx.
		//Clauses(clause.Locking{Strength: "UPDATE"}).
		Where("id = ?", appliId).
		First(&appli).Error
	return &appli, err
}
func (r *sUpdateClubInfoAppliRepo) ApproveAppli(tx *gorm.DB, appliId int) error {
	return tx.
		Model(&dbstruct.UpdateClubInfoAppli{}).
		Where("id = ?", appliId).
		Update("status", "approved").Error
}

func (r *sUpdateClubInfoAppliRepo) RejectAppli(appliId int, reason string) error {
	return r.database.
		Model(&dbstruct.UpdateClubInfoAppli{}).
		Where("update_appli_id = ?", appliId).
		Select("status", "reason").
		Updates(dbstruct.UpdateClubInfoAppli{
			Status:         "rejected",
			RejectedReason: reason,
		}).Error
}

func (r *sUpdateClubInfoAppliRepo) GetUpdateList(offset, num int) ([]*dbstruct.UpdateClubInfoAppli, error) {
	var applis []*dbstruct.UpdateClubInfoAppli
	err := r.database.
		Offset(offset).
		Limit(num).
		Find(&applis).Error
	return applis, err
}

func (r *sUpdateClubInfoAppliRepo) GetApplisByUserId(userId int) ([]*dbstruct.UpdateClubInfoAppli, error) {
	var applis []*dbstruct.UpdateClubInfoAppli
	err := r.database.
		Where("applicant_id = ?", userId).
		Find(&applis).Error
	return applis, err
}

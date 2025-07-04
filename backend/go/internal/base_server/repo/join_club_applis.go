package repo

import (
	"errors"
	"fmt"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type JoinClubAppliRepo interface {
	AddJoinClubAppli(appli *dbstruct.JoinClubAppli) error
	GetJoinClubAppliList(clubId int) ([]*dbstruct.JoinClubAppli, error)
	GetApplisByUserId(userId int) ([]*dbstruct.JoinClubAppli, error)
	GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.JoinClubAppli, error)
	ApproveAppli(tx *gorm.DB, appliId int) error
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

func (r *sJoinClubAppliRepo) AddJoinClubAppli(appli *dbstruct.JoinClubAppli) error {
	return r.database.Transaction(func(tx *gorm.DB) error {
		var existing dbstruct.JoinClubAppli
		err := tx.
			//Clauses(clause.Locking{Strength: "UPDATE"}).
			Where("user_id = ? AND club_id = ? AND (status = 'pending' OR status = 'approved')",
				appli.UserId, appli.ClubId).
			First(&existing).Error

		if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
			return err
		}

		if existing.JoinAppliId != 0 {
			return fmt.Errorf("用户（user_id: %d） 有未被拒绝的请求（club_id: %d）",
				appli.UserId, appli.ClubId)
		}

		return tx.Create(appli).Error
	})
}

func (r *sJoinClubAppliRepo) GetJoinClubAppliList(clubId int) ([]*dbstruct.JoinClubAppli, error) {
	if clubId <= 0 {
		return nil, errors.New("无效参数")
	}

	var appliList []*dbstruct.JoinClubAppli
	err := r.database.
		Model(&dbstruct.JoinClubAppli{}).
		Where("club_id = ?", clubId).
		Find(&appliList).Error

	return appliList, err
}

func (s *sJoinClubAppliRepo) GetApplisByUserId(userId int) ([]*dbstruct.JoinClubAppli, error) {
	var applis []*dbstruct.JoinClubAppli
	err := s.database.
		Where("user_id = ?", userId).
		Find(&applis).Error
	return applis, err
}

func (r *sJoinClubAppliRepo) GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.JoinClubAppli, error) {
	if appliId <= 0 {
		return nil, errors.New("无效参数")
	}

	var appli dbstruct.JoinClubAppli
	err := tx.
		//Clauses(clause.Locking{Strength: "UPDATE"}).
		Model(&dbstruct.JoinClubAppli{}).
		Where("join_appli_id = ?", appliId).
		Find(&appli).Error

	return &appli, err
}

func (r *sJoinClubAppliRepo) ApproveAppli(tx *gorm.DB, appliId int) error {
	if appliId <= 0 {
		return errors.New("无效参数")
	}

	return r.database.
		Model(&dbstruct.JoinClubAppli{}).
		Where("join_appli_id = ?", appliId).
		Update("status", "approved").Error
}

func (r *sJoinClubAppliRepo) RejectAppli(appliId int, reason string) error {
	return r.database.
		Model(&dbstruct.JoinClubAppli{}).
		Where("join_appli_id = ?", appliId).
		Select("status", "reject_reason").
		Updates(dbstruct.JoinClubAppli{
			Status:         "rejected",
			RejectedReason: reason,
		}).Error
}

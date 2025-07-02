package repo

import (
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type ClubMemberRepo interface {
	CreateClubMember(member *dbstruct.ClubMember) error
	AppendClubMember(tx *gorm.DB, member *dbstruct.ClubMember) error
	GetClubMemberList(offset, num int) ([]*dbstruct.ClubMember, error)
	GetClubMemberInfo(id int) (*dbstruct.ClubMember, error)
	GetMemberListByClubId(clubId int) ([]*dbstruct.ClubMember, error)
	GetClubListByUserId(userId int) ([]*dbstruct.Club, error)
}

type sClubMemberRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateClubMemberRepo(
	database *gorm.DB,
	logger *slog.Logger,
) ClubMemberRepo {
	return &sClubMemberRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sClubMemberRepo) CreateClubMember(member *dbstruct.ClubMember) error {
	return r.database.Create(member).Error
}

func (r *sClubMemberRepo) AppendClubMember(tx *gorm.DB, member *dbstruct.ClubMember) error {
	return tx.Create(member).Error
}

func (r *sClubMemberRepo) GetClubMemberList(offset, num int) ([]*dbstruct.ClubMember, error) {
	var members []*dbstruct.ClubMember
	err := r.database.
		Offset(offset).
		Limit(num).
		Find(&members).Error
	return members, err
}

func (r *sClubMemberRepo) GetClubMemberInfo(id int) (*dbstruct.ClubMember, error) {
	var member dbstruct.ClubMember
	err := r.database.
		Where("member_id = ?", id).
		First(&member).Error
	return &member, err
}

func (r *sClubMemberRepo) GetMemberListByClubId(clubId int) ([]*dbstruct.ClubMember, error) {
	var members []*dbstruct.ClubMember
	err := r.database.
		Where("club_id = ?", clubId).
		Find(&members).Error
	return members, err
}

func (r *sClubMemberRepo) GetClubListByUserId(userId int) ([]*dbstruct.Club, error) {
	var members []*dbstruct.ClubMember
	err := r.database.
		Model(&dbstruct.ClubMember{}).
		Where("user_id = ?", userId).
		Find(&members).Error
	if err != nil {
		return nil, err
	}

	var clubs []*dbstruct.Club
	for _, m := range members {
		var club dbstruct.Club
		err := r.database.
			Model(&dbstruct.Club{}).
			Where("club_id = ?", m.ClubId).
			Find(&club).Error
		if err != nil {
			return nil, err
		}

		clubs = append(clubs, &club)
	}

	return clubs, nil
}

package service

import (
	"context"
	"errors"
	"log/slog"
	"time"
	"whuclubsynapse-server/internal/base_server/repo"
	"whuclubsynapse-server/internal/shared/dbstruct"
	"whuclubsynapse-server/internal/shared/jsonbutil"

	"gorm.io/gorm"
)

type ClubService interface {
	GetClubList(offset, num int) ([]*dbstruct.Club, error)
	GetClubInfo(clubId int) (*dbstruct.Club, error)
	GetClubsByCategory(catId int) ([]*dbstruct.Club, error)
	GetLatestClubs() ([]*dbstruct.Club, error)
	GetClubNum() (int64, error)
	GetClubCategories() ([]*dbstruct.Category, error)

	GetJoinApplisForClub(clubId int) ([]*dbstruct.JoinClubAppli, error)
	GetCreateApplisForUser(userId int) ([]*dbstruct.CreateClubAppli, error)

	GetUserCreateApplis(userId int) ([]*dbstruct.CreateClubAppli, error)
	GetUserJoinApplis(userId int) ([]*dbstruct.JoinClubAppli, error)

	GetMemberList(clubId int) ([]*dbstruct.ClubMember, error)
	GetClubListByUserId(userId int) ([]*dbstruct.Club, error)

	ApplyForCreateClub(newClub dbstruct.Club) error
	ApplyForJoinClub(userId, expectedClubId uint, reason string) error
	ApplyForUpdateClub(newInfo dbstruct.Club) error

	ApproveAppliForCreateClub(appliId int) (uint, error)
	RejectAppliForCreateClub(appliId int, reason string) error

	ApproveAppliForJoinClub(appliId int) error
	RejectAppliForJoinClub(appliId int, reason string) error

	ApproveAppliForUpdateClub(appliId int) error
	RejectAppliForUpdateClub(appliId int, reason string) error

	FavouriteClub(userId, clubId int) error
	UnfavouriteClub(userId, clubId int) error
	GetFavoriteClubs(userId int) ([]*dbstruct.Club, error)

	UpdateClubLogo(clubId int, logoUrl string) error

	QuitClub(clubId, userId int) error
	DissambleClub(clubId int) error

	GetUpdateApplisForUser(userId int) ([]*dbstruct.UpdateClubInfoAppli, error)
	GetUpdateList(offset, num int) ([]*dbstruct.UpdateClubInfoAppli, error)
}

type sClubService struct {
	userRepo                repo.UserRepo
	clubRepo                repo.ClubRepo
	clubMemberRepo          repo.ClubMemberRepo
	clubPostRepo            repo.ClubPostRepo
	createClubAppliRepo     repo.CreateClubAppliRepo
	joinClubAppliRepo       repo.JoinClubAppliRepo
	categoryRepo            repo.CatogoryRepo
	updateClubInfoAppliRepo repo.UpdateClubInfoAppliRepo
	clubFavoriteRepo        repo.ClubFavouriteRepo

	txCoordinator repo.TransactionCoordinator

	logger *slog.Logger
}

func NewClubService(
	userRepo repo.UserRepo,
	clubRepo repo.ClubRepo,
	clubMemberRepo repo.ClubMemberRepo,
	clubPostRepo repo.ClubPostRepo,
	createClubAppliRepo repo.CreateClubAppliRepo,
	joinClubAppliRepo repo.JoinClubAppliRepo,
	categoryRepo repo.CatogoryRepo,
	updateClubInfoAppliRepo repo.UpdateClubInfoAppliRepo,
	clubFavoriteRepo repo.ClubFavouriteRepo,

	txCoordinator repo.TransactionCoordinator,

	logger *slog.Logger,
) ClubService {
	return &sClubService{
		userRepo:                userRepo,
		clubRepo:                clubRepo,
		clubMemberRepo:          clubMemberRepo,
		clubPostRepo:            clubPostRepo,
		createClubAppliRepo:     createClubAppliRepo,
		joinClubAppliRepo:       joinClubAppliRepo,
		categoryRepo:            categoryRepo,
		updateClubInfoAppliRepo: updateClubInfoAppliRepo,
		clubFavoriteRepo:        clubFavoriteRepo,

		txCoordinator: txCoordinator,

		logger: logger,
	}
}

func (s *sClubService) GetClubList(offset, num int) ([]*dbstruct.Club, error) {
	return s.clubRepo.GetClubList(offset, num)
}

func (s *sClubService) GetClubInfo(clubId int) (*dbstruct.Club, error) {
	return s.clubRepo.GetClubInfo(clubId)
}

func (s *sClubService) GetClubsByCategory(catId int) ([]*dbstruct.Club, error) {
	return s.clubRepo.GetClubsByCategory(catId)
}

func (s *sClubService) GetLatestClubs() ([]*dbstruct.Club, error) {
	return s.clubRepo.GetLatestClubs()
}

func (s *sClubService) GetClubNum() (int64, error) {
	return s.clubRepo.GetClubNum()
}

func (s *sClubService) GetClubCategories() ([]*dbstruct.Category, error) {
	return s.categoryRepo.GetCategoryList()
}

func (s *sClubService) GetUserCreateApplis(userId int) ([]*dbstruct.CreateClubAppli, error) {
	return s.createClubAppliRepo.GetApplisByUserId(userId)
}

func (s *sClubService) GetUserJoinApplis(userId int) ([]*dbstruct.JoinClubAppli, error) {
	return s.joinClubAppliRepo.GetApplisByUserId(userId)
}

func (s *sClubService) GetMemberList(clubId int) ([]*dbstruct.ClubMember, error) {
	return s.clubMemberRepo.GetMemberListByClubId(clubId)
}

func (s *sClubService) GetClubListByUserId(userId int) ([]*dbstruct.Club, error) {
	return s.clubMemberRepo.GetClubListByUserId(userId)
}

func (s *sClubService) ApplyForCreateClub(newClub dbstruct.Club) error {
	jsonbClub, err := jsonbutil.ToJsonb(newClub)
	if err != nil {
		return err
	}

	appli := dbstruct.CreateClubAppli{
		UserId:   uint(newClub.LeaderId),
		Proposal: jsonbClub,
	}

	return s.createClubAppliRepo.AddCreateClubAppli(&appli)
}

func (s *sClubService) ApplyForJoinClub(userId, expectedClubId uint, reason string) error {
	s.logger.Info("申请加入社团", "user_id", userId, "club_id", expectedClubId)
	return s.joinClubAppliRepo.AddJoinClubAppli(&dbstruct.JoinClubAppli{
		UserId:      userId,
		ClubId:      expectedClubId,
		ApplyReason: reason,
	})
}

func (s *sClubService) ApplyForUpdateClub(newInfo dbstruct.Club) error {
	jsonbClub, err := jsonbutil.ToJsonb(newInfo)
	if err != nil {
		return err
	}

	appli := dbstruct.UpdateClubInfoAppli{
		ClubId:      uint(newInfo.ClubId),
		ApplicantId: newInfo.LeaderId,
		Proposal:    jsonbClub,
	}

	return s.updateClubInfoAppliRepo.AddUpdateClubInfoAppli(&appli)
}

func (s *sClubService) ApproveAppliForCreateClub(appliId int) (uint, error) {
	ctxTmt, cancel := context.WithTimeout(context.Background(), 1000*time.Second)
	defer cancel()

	var newClubId uint

	err := s.txCoordinator.RunInTransaction(ctxTmt, func(tx *gorm.DB) error {
		appli, err := s.createClubAppliRepo.GetAppliForUpdate(tx, appliId)
		if err != nil {
			return err
		}

		if appli.Status != "pending" {
			return errors.New("申请无法处理")
		}

		if err := s.createClubAppliRepo.ApproveAppli(tx, appliId); err != nil {
			return err
		}

		var newClub dbstruct.Club
		if err := jsonbutil.FromJsonb(appli.Proposal, &newClub); err != nil {
			return err
		}

		if err := s.clubRepo.AppendClub(tx, &newClub); err != nil {
			return err
		}

		if err := s.userRepo.UpdateUserRole(
			tx, int(appli.UserId), dbstruct.ROLE_CLUB_LEADER); err != nil {
			return err
		}

		if err := s.clubMemberRepo.AppendClubMember(tx, &dbstruct.ClubMember{
			ClubId:     newClub.ClubId,
			UserId:     appli.UserId,
			RoleInClub: dbstruct.ROLE_CLUB_LEADER,
		}); err != nil {
			return err
		}

		newClubId = newClub.ClubId

		return nil
	})
	if err != nil {
		return 0, err
	}

	return newClubId, nil
}

func (s *sClubService) RejectAppliForCreateClub(appliId int, reason string) error {
	return s.createClubAppliRepo.RejectAppli(appliId, reason)
}

func (s *sClubService) ApproveAppliForJoinClub(appliId int) error {
	ctxTmt, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return s.txCoordinator.RunInTransaction(ctxTmt, func(tx *gorm.DB) error {
		appli, err := s.joinClubAppliRepo.GetAppliForUpdate(tx, appliId)
		if err != nil {
			return err
		}

		userId := appli.UserId
		clubId := appli.ClubId

		if err := s.clubMemberRepo.AppendClubMember(tx, &dbstruct.ClubMember{
			ClubId: clubId,
			UserId: userId,
		}); err != nil {
			return err
		}

		return s.joinClubAppliRepo.ApproveAppli(tx, appliId)
	})
}

func (s *sClubService) RejectAppliForJoinClub(appliId int, reason string) error {
	return s.joinClubAppliRepo.RejectAppli(appliId, reason)
}

func (s *sClubService) ApproveAppliForUpdateClub(appliId int) error {
	ctxTmt, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return s.txCoordinator.RunInTransaction(ctxTmt, func(tx *gorm.DB) error {
		appli, err := s.updateClubInfoAppliRepo.GetAppliForUpdate(tx, appliId)
		if err != nil {
			return err
		}

		return s.clubRepo.UpdateClubInfo(tx, appli.Club)
	})
}

func (s *sClubService) RejectAppliForUpdateClub(appliId int, reason string) error {
	return s.createClubAppliRepo.RejectAppli(appliId, reason)
}

func (s *sClubService) FavouriteClub(userId, clubId int) error {
	return s.clubFavoriteRepo.AddClubFavourite(userId, clubId)
}

func (s *sClubService) UnfavouriteClub(userId, clubId int) error {
	return s.clubFavoriteRepo.RemoveClubFavourite(userId, clubId)
}

func (s *sClubService) GetFavoriteClubs(userId int) ([]*dbstruct.Club, error) {
	clubsIds, err := s.clubFavoriteRepo.GetClubFavorites(userId)
	if err != nil {
		return nil, err
	}

	var clubs []*dbstruct.Club
	for _, clubId := range clubsIds {
		club, err := s.clubRepo.GetClubInfo(int(clubId))
		if err != nil {
			return nil, err
		}
		clubs = append(clubs, club)
	}

	return clubs, nil
}

func (s *sClubService) GetJoinApplisForClub(clubId int) ([]*dbstruct.JoinClubAppli, error) {
	return s.joinClubAppliRepo.GetJoinClubAppliList(clubId)
}

func (s *sClubService) GetCreateApplisForUser(userId int) ([]*dbstruct.CreateClubAppli, error) {
	return s.createClubAppliRepo.GetCreateClubAppliList(userId)
}

func (s *sClubService) UpdateClubLogo(clubId int, logoUrl string) error {
	return s.clubRepo.UpdateClubLogo(clubId, logoUrl)
}

func (s *sClubService) QuitClub(clubId, userId int) error {
	return s.clubMemberRepo.DeleteMember(userId, clubId)
}

func (s *sClubService) DissambleClub(clubId int) error {
	ctxTmt, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return s.txCoordinator.RunInTransaction(ctxTmt, func(tx *gorm.DB) error {
		if err := s.clubMemberRepo.DeleteClub(tx, clubId); err != nil {
			return err
		}

		if err := s.clubRepo.DeleteClub(clubId); err != nil {
			return err
		}

		return nil
	})
}

func (s *sClubService) GetUpdateApplisForUser(userId int) ([]*dbstruct.UpdateClubInfoAppli, error) {
	return s.updateClubInfoAppliRepo.GetApplisByUserId(userId)
}

func (s *sClubService) GetUpdateList(offset, num int) ([]*dbstruct.UpdateClubInfoAppli, error) {
	return s.updateClubInfoAppliRepo.GetUpdateList(offset, num)
}

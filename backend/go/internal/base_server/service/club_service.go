package service

import (
	"log/slog"
	"whuclubsynapse-server/internal/base_server/repo"
	"whuclubsynapse-server/internal/shared/dbstruct"
)

type ClubService interface {
	GetClubList(offset, num int) ([]*dbstruct.Club, error)
	GetClubInfo(clubId int) (*dbstruct.Club, error)
	GetClubsByCategory(catId int) ([]*dbstruct.Club, error)
	GetLatestClubs() ([]*dbstruct.Club, error)
	GetMemberList(clubId int) ([]*dbstruct.ClubMember, error)
	GetClubListByUserId(userId int) ([]*dbstruct.Club, error)
	GetClubPostList(clubId int) ([]*dbstruct.ClubPost, error)

	ApplyForCreateClub(newClub dbstruct.Club) error
	ApplyForJoinClub(userId, expectedClubId uint) error

	ApproveAppliForCreateClub(appliId int) error
	RejectAppliForCreateClub(appliId int, reason string) error

	ApproveAppliForJoinClub(appliId int) error
	RejectAppliForJoinClub(appliId int, reason string) error

	UpdateClubInfo(newInfo dbstruct.Club) error
}

type sClubService struct {
	clubRepo            repo.ClubRepo
	clubMemberRepo      repo.ClubMemberRepo
	clubPostRepo        repo.ClubPostRepo
	createClubAppliRepo repo.CreateClubAppliRepo
	joinClubAppliRepo   repo.JoinClubAppliRepo
	categoryRepo        repo.CatogoryRepo

	logger *slog.Logger
}

func NewClubService(
	clubRepo repo.ClubRepo,
	clubMemberRepo repo.ClubMemberRepo,
	clubPostRepo repo.ClubPostRepo,
	createClubAppliRepo repo.CreateClubAppliRepo,
	joinClubAppliRepo repo.JoinClubAppliRepo,
	categoryRepo repo.CatogoryRepo,

	logger *slog.Logger,
) ClubService {
	return &sClubService{
		clubRepo:            clubRepo,
		clubMemberRepo:      clubMemberRepo,
		clubPostRepo:        clubPostRepo,
		createClubAppliRepo: createClubAppliRepo,
		joinClubAppliRepo:   joinClubAppliRepo,
		categoryRepo:        categoryRepo,

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

func (s *sClubService) GetMemberList(clubId int) ([]*dbstruct.ClubMember, error) {
	return s.clubMemberRepo.GetMemberListByClubId(clubId)
}

func (s *sClubService) GetClubListByUserId(userId int) ([]*dbstruct.Club, error) {
	return s.clubMemberRepo.GetClubListByUserId(userId)
}

func (s *sClubService) GetClubPostList(clubId int) ([]*dbstruct.ClubPost, error) {
	return s.clubPostRepo.GetClubPostList(clubId)
}

func (s *sClubService) ApplyForCreateClub(newClub dbstruct.Club) error {
	err := s.clubRepo.AddClub(newClub)
	if err != nil {
		return err
	}

	return s.createClubAppliRepo.AddCreateClubAppli(dbstruct.CreateClubApplication{
		UserId: newClub.LeaderId,
	})
}

func (s *sClubService) ApplyForJoinClub(userId, expectedClubId uint) error {
	return s.joinClubAppliRepo.AddJoinClubAppli(dbstruct.JoinClubApplication{
		UserId: userId,
		ClubId: expectedClubId,
	})
}

func (s *sClubService) ApproveAppliForCreateClub(appliId int) error {
	return s.createClubAppliRepo.ApproveAppli(appliId)
}

func (s *sClubService) RejectAppliForCreateClub(appliId int, reason string) error {
	return s.createClubAppliRepo.RejectAppli(appliId, reason)
}

func (s *sClubService) ApproveAppliForJoinClub(appliId int) error {
	return s.joinClubAppliRepo.ApproveAppli(appliId)
}

func (s *sClubService) RejectAppliForJoinClub(appliId int, reason string) error {
	return s.joinClubAppliRepo.RejectAppli(appliId, reason)
}

func (s *sClubService) UpdateClubInfo(newInfo dbstruct.Club) error {
	return s.clubRepo.UpdateClubInfo(newInfo)
}

package dto

type FavoriteClubRequest struct {
	ClubId int `json:"club_id"`
}

type UnfavoriteClubRequest struct {
	ClubId int `json:"club_id"`
}

package dto

type ClubMember struct {
	MemberId   int    `json:"member_id"`
	UserId     int    `json:"user_id"`
	ClubId     int    `json:"club_id"`
	RoleInClub string `json:"role_in_club"`
	JoinedAt   string `json:"joined_at"`
	LastActive string `json:"last_active"`
}

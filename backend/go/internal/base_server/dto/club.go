package dto

type ClubBasic struct {
	ClubId      int    `json:"club_id"`
	ClubName    string `json:"club_name"`
	Category    int    `json:"category"`
	LogoUrl     string `json:"logo_url"`
	Desc        string `json:"desc"`
	CreatedAt   string `json:"created_at"`
	MemberCount int    `json:"member_count"`
}

type ClubDetail struct {
	ClubBasic
	Members []*ClubMember    `json:"members"`
	Posts   []*ClubPostBasic `json:"posts"`
}

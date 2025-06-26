package dto

type ClubBasic struct {
	ClubId   int    `json:"club_id"`
	ClubName string `json:"club_name"`
	Category string `json:"category"`
	LogoUrl  string `json:"logo_url"`
	Desc     string `json:"desc"`
}

type ClubDetail struct {
	ClubBasic
	Members []*ClubMember    `json:"members"`
	Posts   []*ClubPostBasic `json:"posts"`
}

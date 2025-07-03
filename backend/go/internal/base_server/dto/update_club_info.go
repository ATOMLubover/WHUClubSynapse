package dto

type UpdateClubInfoRequest struct {
	Name         string   `json:"name"`
	Desc         string   `json:"desc"`
	Requirements string   `json:"requirements"`
	CatogoryId   int      `json:"category_id"`
	Tags         []string `json:"tags"`
}

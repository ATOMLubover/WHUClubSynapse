package dto

type CreateClubAppliRequest struct {
	Name         string `json:"name"`
	Desc         string `json:"desc"`
	Requirements string `json:"requirements"`
}

package dto

type CreateClubAppliRequest struct {
	Name         string `json:"name"`
	Desc         string `json:"desc"`
	CategoryId   int    `json:"category_id"`
	Tags         string `json:"tags"`
	Requirements string `json:"requirements"`
}

type CreateClubAppliResponse struct {
	AppliId      int    `json:"appli_id"`
	AppliedAt    string `json:"applied_at"`
	Status       string `json:"status"`
	RejectReason string `json:"reject_reason"`
	ReviewedAt   string `json:"reviewed_at"`
}

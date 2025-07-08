package dto

type UpdateClubInfoRequest struct {
	Name         string   `json:"name"`
	Desc         string   `json:"desc"`
	Requirements string   `json:"requirements"`
	CatogoryId   int      `json:"category_id"`
	Tags         []string `json:"tags"`
}

type UpdateClubInfoResponse struct {
	Proposal       string `json:"proposal"`
	Status         string `json:"status"`
	AppliId        int    `json:"appli_id"`
	RejectedReason string `json:"rejected_reason"`
}

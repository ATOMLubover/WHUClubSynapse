package dto

type JoinClubAppliResponse struct {
	AppliId      int    `json:"appli_id"`
	AppliedAt    string `json:"applied_at"`
	Status       string `json:"status"`
	RejectReason string `json:"reject_reason"`
	ReviewedAt   string `json:"reviewed_at"`
}

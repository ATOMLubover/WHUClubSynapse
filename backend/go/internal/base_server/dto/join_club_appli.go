package dto

type JoinClubAppliRequest struct {
	Reason string `json:"reason"`
}

type JoinClubAppliResponse struct {
	AppliId      int    `json:"appli_id"`
	AppliedAt    string `json:"applied_at"`
	ClubId       int    `json:"club_id"`
	ApplicantId  int    `json:"applicant_id"`
	Reason       string `json:"reason"`
	Status       string `json:"status"`
	RejectReason string `json:"reject_reason"`
	ReviewedAt   string `json:"reviewed_at"`
}

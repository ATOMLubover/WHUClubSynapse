package dto

type ProcJoinClubRequest struct {
	JoinAppliId int    `json:"join_appli_id"`
	Result      string `json:"result"`
	Reason      string `json:"reason"`
}

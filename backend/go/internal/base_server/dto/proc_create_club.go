package dto

type ProcCreateClubRequest struct {
	CreateClubAppliId int    `json:"create_club_appli_id"`
	Result            string `json:"result"`
	Reason            string `json:"reason"`
}

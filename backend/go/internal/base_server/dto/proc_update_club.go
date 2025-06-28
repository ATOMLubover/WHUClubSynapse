package dto

type ProcUpdateClubRequest struct {
	UpdateAppliId int    `json:"update_appli_id"`
	Result        string `json:"result"`
	Reason        string `json:"reason"`
}

# -*- coding: utf8 -*-

logs = {
     "msk-func":
     {
	  "msk-func-01": ["Application","CRM.Gateway", "CRM_Errors",
		  "CRM_Interfaces", "Foris.Catalogues", "FORIS.Common",
		  "FORIS.Production", "FORIS.RemoteDealer", "FORIS.Sales",
		  "FORIS.ScratchCards", "FORIS.ScratchCards.Activation",
		  "Foris.SelfCare", "FORIS.TelCRM.GUI", "Foris.TelCRM.Marketing",
		  "Foris.TelCrm.RequestManagement", "FORIS.TelCRM.Sales",
		  "ForwardedEvents", "Marti.CommunityManagementUI",
		  "Marti.OrderCatalogueUI",
		  "Microsoft-Windows-EventCollector/Operational",
		  "Microsoft-Windows-Forwarding/Operational", "System",
		  "TelCRM.Marketing", "TelCRM.Production", "Windows PowerShell"],
	  "msk-func-02": ["Application","CRM.Gateway", "FORIS.Billing",
		  "Foris.Catalogues", "FORIS.Common", "FORIS.TelCRM.Sales",
		  "FORIS.UPRSGateway", "System"],
	  "msk-func-03": ["Application","CRM.Gateway", "Foris.Catalogues",
		  "FORIS.Common", "Foris.RDExtension", "Foris.REService",
		  "Foris.ServiceRDExtension", "FORIS.StateIn.SQR", "FORIS.SUPS.OTSP",
		  "FORIS.SUPS.PSP.INTimer", "FORIS.SUPS.PSP.TelCRMInteraction",
		  "FORIS.SUPS.PSP.Timer", "FORIS.SUPS.SPF.ProcUnit",
		  "FORIS.SUPS.SPFMonitoring", "FORIS.SUPS.SPFServer",
		  "FORIS.SUPS.StateIn", "FORIS.SUPS.StateIn.BonusSystem",
		  "FORIS.UMRS.CRM", "FORIS.UMRS.DataLoaderFailover", "FORIS.UMRS.DOC",
		  "Intercept", "System"],
	  "msk-func-04": ["Application","Foris.Catalogues", "FORIS.Common",
		  "Foris.ODS", "Foris.RDExtension", "FORIS.RI", "Foris.SelfCare",
		  "FORIS.Stock", "FORIS_Scheduler", "FORIS_Security", "Intercept",
		  "System"],
	  "msk-func-05": ["Application","CRM.Gateway", "Foris.Catalogues",
		  "FORIS.Common", "FORIS.DataBus", "FORIS.MessagingGateway",
		  "FORIS.TelBill.DOC", "System"],
	  "msk-func-06": ["Application","CRM.Gateway", "Foris.Catalogues", "FORIS.Common", "Foris.SPA.BPM", "Foris.SPA.Disp", "Foris.SPA.Monitor", "Foris.SPA.SA", "Foris.SPA.ScenarioEditor", "Foris.SPA.Sync", "SPA.Disp", "System"],
	  "msk-func-07": ["Application","FORIS.Billing", "Foris.Catalogues",
		  "FORIS.Common", "Foris.ODS", "FORIS.ResourceLocking", "FORIS.RI",
		  "FORIS.ServiceRegistry", "FORIS.Workflow", "System"],
	  "msk-func-08": ["Application","FORIS.Billing", "Foris.Catalogues",
		  "FORIS.Common", "Foris.ODS", "FORIS.ResourceLocking", "FORIS.RI",
		  "FORIS.ServiceRegistry", "FORIS.Workflow", "System"],
	  "msk-func-09": ["Application","FORIS.Common", "FORIS.ResourceLocking",
		  "FORIS.ServiceRegistry", "FORIS.Workflow", "Intercept", "Security",
		  "System"],
	  "msk-func-10": ["Application","FORIS.Common", "Foris.SelfCare",
		  "System"],
	  "msk-func-11": ["Application","FORIS.Billing", "Foris.Catalogues",
		  "FORIS.Common", "Foris.ODS", "Foris.REService", "FORIS.RI",
		  "System"],
	  "msk-func-12": ["Application","CRM.Gateway", "Foris.Catalogues", "FORIS.Common", "Foris.PasswordSecurity", "FORIS.TelBill.DOC", "System"]
     },
     "nag-tc" : 
     {
	"nag-tc-01": ["Application","CRM.Gateway", "CRM_Errors", "CRM_Interfaces", "Foris.Catalogues", "FORIS.Common", "FORIS.Production", "FORIS.ResourceLocking", "FORIS.Sales", "FORIS.ScratchCards", "FORIS.ScratchCards.Activation", "Foris.SelfCare", "FORIS.TelCRM.GUI", "Foris.TelCRM.Marketing", "Foris.TelCrm.RequestManagement", "FORIS.TelCRM.Sales", "FORIS.Workflow", "Marti.CommunityManagementUI", "Marti.OrderCatalogueUI", "System", "TelCRM.Marketing", "TelCRM.Production", "TelCRM.WindowsServices"],
	"nag-tc-02": ["Application","CAFToolCollection", "CRM.Gateway", "FinFraud", "FORIS.Billing", "FORIS.Catalogues", "FORIS.Common", "FORIS.DataBus", "FORIS.PerformanceInstaller", "FORIS.SUPS.OTSP", "FORIS.SUPS.PSP.INTimer", "FORIS.SUPS.PSP.TelCRMInteraction", "FORIS.SUPS.PSP.Timer", "FORIS.SUPS.SPF.ProcUnit", "FORIS.SUPS.SPFMonitoring", "FORIS.SUPS.SPFServer", "FORIS.SUPS.StateIn", "FORIS.SUPS.StateIn.BonusSystem", "FORIS.UPRSGateway", "FORIS_Security", "IModeRouter.Log", "Operations Manager", "ParentApp", "SessionSecurityManagement", "System"],
	"nag-tc-03": ["Application","CRM.Gateway", "Foris.Catalogues", "FORIS.Common", "Foris.RDExtension", "Foris.REService", "Foris.ServiceRDExtension", "FORIS.StateIn.SQR", "FORIS.SUPS.OTSP", "FORIS.SUPS.PSP.INTimer", "FORIS.SUPS.PSP.TelCRMInteraction", "FORIS.SUPS.PSP.Timer", "FORIS.SUPS.SPF.ProcUnit", "FORIS.SUPS.SPFMonitoring", "FORIS.SUPS.SPFServer", "FORIS.SUPS.StateIn", "FORIS.SUPS.StateIn.BonusSystem", "FORIS.UMRS.CRM", "FORIS.UMRS.DataLoaderFailover", "FORIS.UMRS.DOC", "Intercept", "System"],
	"nag-tc-04": ["Application","CRM.Gateway", "FORIS.Catalogues", "FORIS.Common", "Foris.ODS", "Foris.RDExtension", "FORIS.RI", "FORIS.Stock", "FORIS_Scheduler", "FORIS_Security", "Operations Manager", "RDExtensionLog","Services", "System", "Windows PowerShell"],
	"nag-tc-05": ["Application","FORIS.Common", "FORIS.MessagingGateway", "System"],
	"nag-tc-06": ["Application","BPMLog", "bpm_02_20080611_N34.mdb", "CRM.Gateway", "FORIS.Catalogues", "FORIS.Common", "FORIS.PerformanceInstaller", "FORIS.Sales", "Foris.SPA.BPM", "Foris.SPA.Disp", "Foris.SPA.Monitor", "Foris.SPA.ScenarioEditor", "Foris.SPA.Sync", "FORIS_Security", "Operations Manager", "SelfCare", "SPA.BPM.01", "SPA.Disp", "SPA.Emulator", "SPA.Monitor.New", "SPA.MsgDisp", "SPA.SA.DMS", "SPA.SA.FMC.01", "SPA.SA.HLR.Siemens.SR10.01", "SPA.SA.IMODE.NEC", "SPA.SA.MMSC.LogicaCMG", "SPA.SA.RBT.NEC", "SPA.SA.Siemens.SR10", "SPA.SA.VM.Comverse", "System", "TelCRM.RemoteDealer", "TelCRM.Sales"],
	"nag-tc-07": ["Application","CRM.Gateway", "FORIS Rating Engine", "FORIS.Common", "Foris.PasswordSecurity", "Foris.TelCrm.RequestManagement", "FORIS_Security", "System"],
	"nag-tc-08": ["Application","FORIS.Billing", "FORIS.Catalogues", "FORIS.Common", "Foris.ODS", "FORIS.RI", "Foris.TelCrm.RequestManagement", "System"],
	"nag-tc-09": ["Application","FORIS.Common", "FORIS.ResourceLocking", "FORIS.ServiceRegistry", "FORIS.Workflow", "System"],
	"nag-tc-10": ["Application","Foris.Catalogues", "FORIS.Common", "Foris.SPA.SA", "Foris.SPA.ScenarioEditor", "Foris.SPA.Sync", "System"],
	"nag-tc-11": ["Application","BPMLog", "bpm_02_20080611_N34.mdb", "CRM.Gateway", "CRM_Interfaces", "FORIS.Billing", "FORIS.Catalogues", "FORIS.Common", "Foris.ODS", "FORIS.RI", "FORIS.Sales", "FORIS.SUPS.OTSP", "FORIS.SUPS.PSP.INTimer", "FORIS.SUPS.PSP.TelCRMInteraction", "FORIS.SUPS.PSP.Timer", "FORIS.SUPS.SPF.ProcUnit", "FORIS.SUPS.SPFMonitoring", "FORIS.SUPS.SPFServer", "FORIS.SUPS.StateIn", "FORIS.SUPS.StateIn.BonusSystem", "FORIS.TelBill.DOC", "FORIS.TelCRM.GUI", "Foris.TelCrm.RequestManagement", "FORIS_Security", "Operations Manager", "PLUGINS", "SelfCare", "SPA.BPM.01", "SPA.Monitor.New", "SPA.MsgDisp", "SPA.SA.DMS", "SPA.SA.FMC.01", "SPA.SA.HLR.Siemens.SR10.01", "SPA.SA.IMODE.NEC", "SPA.SA.MMSC.LogicaCMG", "SPA.SA.RBT.NEC", "SPA.SA.Siemens.SR10", "SPA.SA.VM.Comverse", "System", "TelCRM.RemoteDealer", "TelCRM.Sales"],
	"nag-tc-12": ["Application","CRM.Gateway", "Foris.Catalogues", "FORIS.Common", "Foris.PasswordSecurity", "FORIS.TelBill.DOC", "System"]
   },
    "local": {
        "user-pc": ["Application", "System"]
    },
    "umc-test-2": {
        "msk-app-v190": ["Application", "CRM.Gateway", "CRM_Interfaces", "FirscallVCardServiceLog",
"FORIS.Catalogues", "FORIS.Common", "FORIS.Production", "FORIS.Sales",
"FORIS.ScratchCards", "FORIS.ScratchCards.Activation", "Foris.SelfCare",
"FORIS.TelCRM.GUI", "Foris.TelCRM.Marketing", "FORIS.TelCRM.RequestManagement",
"FORIS.TelCRM.Sales", "FORIS_Security", "Marti.CommunityManagementUI",
"Marti.OrderCatalogueUI", "MGALog", "PackageUI", "PrepMntr Log", "PrepServ
Log", "System", "TelCRM.CustomerManagement", "TelCRM.Production",
"TelCRM.WindowsServices"]
    }
}


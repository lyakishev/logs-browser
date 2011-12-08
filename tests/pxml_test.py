# -*- coding: utf8 -*-
import unittest
import sys
import os
import difflib
sys.path.append(os.path.abspath('../logsbrowser'))
from utils.pxml import *

xmls = [
("""[DEBUG][2011-12-07 09:23:39,701][42] Step end AggregateProducts
<callTime>00:00:00</callTime>
<sourceTypeIds><Int32>4</Int32></sourceTypeIds>
----------""",
"""[DEBUG][2011-12-07 09:23:39,701][42] Step end AggregateProducts
<callTime>00:00:00</callTime>
<sourceTypeIds>
    <Int32>4</Int32>
</sourceTypeIds>
----------"""),

("""2011-12-07 09:51:55,641 [44] DEBUG
=======================================
InterconnectionService: The subscriber FORIS.TelCRM.RequestManagement.CustomerCare.JoinPABulk.TransferTDChild.TransferTDChildProcessing processed successfully the following message:
<?xml version="1.0" encoding="utf-16"?><MessageBase xmlns:i="http://www.w3.org/2001/XMLSchema-instance" i:type="BalanceChangedMessage" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001"><RequestId>3000137572</RequestId><RequestTypeCode>TransferTDChild</RequestTypeCode><PersonalAccountNumber>277300018417</PersonalAccountNumber></MessageBase>
=======================================""",
"""2011-12-07 09:51:55,641 [44] DEBUG
=======================================
InterconnectionService: The subscriber FORIS.TelCRM.RequestManagement.CustomerCare.JoinPABulk.TransferTDChild.TransferTDChildProcessing processed successfully the following message:
<?xml version="1.0" encoding="utf-16"?>
<MessageBase xmlns:i="http://www.w3.org/2001/XMLSchema-instance" i:type="BalanceChangedMessage" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001">
    <RequestId>3000137572</RequestId>
    <RequestTypeCode>TransferTDChild</RequestTypeCode>
    <PersonalAccountNumber>277300018417</PersonalAccountNumber>
</MessageBase>
======================================="""),

("""[2011-12-07 09:39:11,893][46] (DEBUG)  Check param BlockDocumentCode - <?xml version="1.0" encoding="utf-16"?><ArrayOfString><string>MASS</string></ArrayOfString> for action 20691 True""",
"""[2011-12-07 09:39:11,893][46] (DEBUG)  Check param BlockDocumentCode - <?xml version="1.0" encoding="utf-16"?>
<ArrayOfString>
    <string>MASS</string>
</ArrayOfString> for action 20691 True"""),

("""2011-12-07 11:42:34,529 [15] DEBUG
=======================================
23066 - GetCustomers - process parameter dtCustomers=<Table></Table>
=======================================""",
"""2011-12-07 11:42:34,529 [15] DEBUG
=======================================
23066 - GetCustomers - process parameter dtCustomers=<Table></Table>
======================================="""),

("""[2011-12-07 11:49:12,130][46] (DEBUG)  Check param ServiceListAlgoritm - <?xml version="1.0" encoding="utf-16"?><ArrayOfString><string>ServicePE</string><string>ServiceOT</string><string>Service_ForSales</string></ArrayOfString> for action 20691 False""",
"""[2011-12-07 11:49:12,130][46] (DEBUG)  Check param ServiceListAlgoritm - <?xml version="1.0" encoding="utf-16"?>
<ArrayOfString>
    <string>ServicePE</string>
    <string>ServiceOT</string>
    <string>Service_ForSales</string>
</ArrayOfString> for action 20691 False"""),

("""[DEBUG][2011-12-07 11:28:06,222][51] Step end GetSecurityInfo
<callTime>00:00:00</callTime>
<securityInfo><AllowedLevel><Level>20</Level><SourceTypeId>4</SourceTypeId><BpCode>SalesContract</BpCode><Enabled>True</Enabled></AllowedLevel><ExcludedLevels></ExcludedLevels></securityInfo>
----------""",

"""[DEBUG][2011-12-07 11:28:06,222][51] Step end GetSecurityInfo
<callTime>00:00:00</callTime>
<securityInfo>
    <AllowedLevel>
        <Level>20</Level>
        <SourceTypeId>4</SourceTypeId>
        <BpCode>SalesContract</BpCode>
        <Enabled>True</Enabled>
    </AllowedLevel>
    <ExcludedLevels></ExcludedLevels>
</securityInfo>
----------"""),

("""2011-12-07 14:45:12,997 [22] DEBUG
=======================================
[call] <FORIS.TelCRM.Interfaces.RI.GetHostByICCIDList> date of start: [07.12.2011 14:45:12] user name: [NT AUTHORITY\NETWORK SERVICE] call parameters: [HL; 07.12.2011 14:45:12; [89700333003330026919]; <?xml version="1.0" encoding="utf-16"?>
<DataTable>
	<DataTable></DataTable>
</DataTable>]
=======================================""",
"""2011-12-07 14:45:12,997 [22] DEBUG
=======================================
[call] <FORIS.TelCRM.Interfaces.RI.GetHostByICCIDList> date of start: [07.12.2011 14:45:12] user name: [NT AUTHORITY\NETWORK SERVICE] call parameters: [HL; 07.12.2011 14:45:12; [89700333003330026919]; <?xml version="1.0" encoding="utf-16"?>
<DataTable>
	<DataTable></DataTable>
</DataTable>]
======================================="""),

("""2011-12-07 09:00:47,836 [8] DEBUG
=======================================
[result] <FORIS.TelCRM.Interfaces.RI.GetHostByICCIDList>  outputs parameters: [<?xml version="1.0" encoding="utf-16"?>
<DataTable>
	<xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
		<xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:MainDataTable="Table1" msdata:Locale="ru-RU">
			<xs:complexType>
				<xs:choice minOccurs="0" maxOccurs="unbounded">
					<xs:element name="Table1" msdata:Locale="ru-RU">
						<xs:complexType></xs:complexType>
					</xs:element>
				</xs:choice>
			</xs:complexType>
		</xs:element>
	</xs:schema>
	<diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1" />
</DataTable>] return value: [null] execution time: [00:00:00.8531755]
=======================================""",
"""2011-12-07 09:00:47,836 [8] DEBUG
=======================================
[result] <FORIS.TelCRM.Interfaces.RI.GetHostByICCIDList>  outputs parameters: [<?xml version="1.0" encoding="utf-16"?>
<DataTable>
	<xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
		<xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:MainDataTable="Table1" msdata:Locale="ru-RU">
			<xs:complexType>
				<xs:choice minOccurs="0" maxOccurs="unbounded">
					<xs:element name="Table1" msdata:Locale="ru-RU">
						<xs:complexType></xs:complexType>
					</xs:element>
				</xs:choice>
			</xs:complexType>
		</xs:element>
	</xs:schema>
	<diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1" />
</DataTable>] return value: [null] execution time: [00:00:00.8531755]
======================================="""),

("""2011-12-07 09:01:21,376 [1] DEBUG
=======================================
-----------------------------------------------
[09:01:21.3768] (Thread=1): Method result GetCustomerById UserName=NT AUTHORITY\NETWORK SERVICE
result: <?xml version="1.0" encoding="utf-16"?><Organization xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sts.sitronics.com/Foris/TelCrm/CustomerManagement/v1/Entities"><Id>47594</Id><DateFrom>2011-12-07T08:49:57</DateFrom><CustomAttributes xmlns:d2p1="http://schemas.marti.sitels.ru/Core/"><d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfBoolNullable"><d2p1:AttributeCode>IsCustomerAddressCorrect</d2p1:AttributeCode><d2p1:TypeCode>Boolean</d2p1:TypeCode><d2p1:TypedValue i:nil="true" /></d2p1:CustomAttribute><d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfString"><d2p1:AttributeCode>Affiliation</d2p1:AttributeCode><d2p1:TypeCode>DictionaryElement</d2p1:TypeCode><d2p1:TypedValue i:nil="true" /></d2p1:CustomAttribute><d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfBoolNullable"><d2p1:AttributeCode>ForbiddenOnInform</d2p1:AttributeCode><d2p1:TypeCode>Boolean</d2p1:TypeCode><d2p1:TypedValue i:nil="true" /></d2p1:CustomAttribute><d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfDecimalNullable"><d2p1:AttributeCode>DealerIdentificatorInSAP</d2p1:AttributeCode><d2p1:TypeCode>Number</d2p1:TypeCode><d2p1:TypedValue i:nil="true" /></d2p1:CustomAttribute><d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfString"><d2p1:AttributeCode>JuridicalReason</d2p1:AttributeCode><d2p1:TypeCode>String</d2p1:TypeCode><d2p1:TypedValue i:nil="true" /></d2p1:CustomAttribute><d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfBoolNullable"><d2p1:AttributeCode>DontSendDateINKB</d2p1:AttributeCode><d2p1:TypeCode>Boolean</d2p1:TypeCode><d2p1:TypedValue i:nil="true" /></d2p1:CustomAttribute></CustomAttributes><VersionDate>2011-12-07T09:01:21</VersionDate><CustomerTypeId>2</CustomerTypeId><CustomerTypeCode>2</CustomerTypeCode><IsPrivate>false</IsPrivate><RegistrationAddressId>7538145</RegistrationAddressId><Inn>3216549873</Inn><Kpp>321564897</Kpp><Note i:nil="true" /><Contracts i:nil="true" /><Contacts i:nil="true" /><AccreditationCards i:nil="true" /><TraceId>152606</TraceId><FactualAddressId>7538145</FactualAddressId><Names i:nil="true" /><Okonh i:nil="true" /><Okpd i:nil="true" /><Okpo i:nil="true" /><RequestId i:nil="true" /></Organization>

=======================================""",
"""2011-12-07 09:01:21,376 [1] DEBUG
=======================================
-----------------------------------------------
[09:01:21.3768] (Thread=1): Method result GetCustomerById UserName=NT AUTHORITY\NETWORK SERVICE
result: <?xml version="1.0" encoding="utf-16"?>
<Organization xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sts.sitronics.com/Foris/TelCrm/CustomerManagement/v1/Entities">
    <Id>47594</Id>
    <DateFrom>2011-12-07T08:49:57</DateFrom>
    <CustomAttributes xmlns:d2p1="http://schemas.marti.sitels.ru/Core/">
        <d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfBoolNullable">
            <d2p1:AttributeCode>IsCustomerAddressCorrect</d2p1:AttributeCode>
            <d2p1:TypeCode>Boolean</d2p1:TypeCode>
            <d2p1:TypedValue i:nil="true" />
        </d2p1:CustomAttribute>
        <d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfString">
            <d2p1:AttributeCode>Affiliation</d2p1:AttributeCode>
            <d2p1:TypeCode>DictionaryElement</d2p1:TypeCode>
            <d2p1:TypedValue i:nil="true" />
        </d2p1:CustomAttribute>
        <d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfBoolNullable">
            <d2p1:AttributeCode>ForbiddenOnInform</d2p1:AttributeCode>
            <d2p1:TypeCode>Boolean</d2p1:TypeCode>
            <d2p1:TypedValue i:nil="true" />
        </d2p1:CustomAttribute>
        <d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfDecimalNullable">
            <d2p1:AttributeCode>DealerIdentificatorInSAP</d2p1:AttributeCode>
            <d2p1:TypeCode>Number</d2p1:TypeCode>
            <d2p1:TypedValue i:nil="true" />
        </d2p1:CustomAttribute>
        <d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfString">
            <d2p1:AttributeCode>JuridicalReason</d2p1:AttributeCode>
            <d2p1:TypeCode>String</d2p1:TypeCode>
            <d2p1:TypedValue i:nil="true" />
        </d2p1:CustomAttribute>
        <d2p1:CustomAttribute i:type="d2p1:CustomAttributeOfBoolNullable">
            <d2p1:AttributeCode>DontSendDateINKB</d2p1:AttributeCode>
            <d2p1:TypeCode>Boolean</d2p1:TypeCode>
            <d2p1:TypedValue i:nil="true" />
        </d2p1:CustomAttribute>
    </CustomAttributes>
    <VersionDate>2011-12-07T09:01:21</VersionDate>
    <CustomerTypeId>2</CustomerTypeId>
    <CustomerTypeCode>2</CustomerTypeCode>
    <IsPrivate>false</IsPrivate>
    <RegistrationAddressId>7538145</RegistrationAddressId>
    <Inn>3216549873</Inn>
    <Kpp>321564897</Kpp>
    <Note i:nil="true" />
    <Contracts i:nil="true" />
    <Contacts i:nil="true" />
    <AccreditationCards i:nil="true" />
    <TraceId>152606</TraceId>
    <FactualAddressId>7538145</FactualAddressId>
    <Names i:nil="true" />
    <Okonh i:nil="true" />
    <Okpd i:nil="true" />
    <Okpo i:nil="true" />
    <RequestId i:nil="true" />
</Organization>

======================================="""),

("""2011-12-07 09:05:23,758 [17] DEBUG FORIS.TelCRM.RemoteDealer.Services.Interfaces.IRequestDirectory
=======================================
[result] <ReceiveRegistrationRequests>  outputs parameters: [<?xml version="1.0" encoding="utf-16"?>
<RequestListDTO xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/FORIS.TelCRM.RemoteDealer.CommonLibrary">
	<ContractNr></ContractNr>
	<Count>20</Count>
	<CrmOperatorID>9912</CrmOperatorID>
	<CustomerFirstName></CustomerFirstName>
	<CustomerLastName></CustomerLastName>
	<CustomerMiddleName></CustomerMiddleName>
	<CustomerTypeID>-1</CustomerTypeID>
	<DateFrom>2011-12-06T09:04:54</DateFrom>
	<DateTo>2011-12-07T09:04:54</DateTo>
	<DealerID>6427</DealerID>
	<ForisOperatorID>-1003</ForisOperatorID>
	<ICCID></ICCID>
	<MSISDN></MSISDN>
	<OrganizationName></OrganizationName>
	<PA></PA>
	<ReqTypesAndPrivileges>
		<ReqTypePrivilege>
			<Privilege>ReceiveCustomerRegistrationDealerRequests</Privilege>
			<ReqType>CustomerRegistration</ReqType>
		</ReqTypePrivilege>
	</ReqTypesAndPrivileges>
	<Reqs>
		<xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
			<xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">
				<xs:complexType>
					<xs:choice minOccurs="0" maxOccurs="unbounded">
						<xs:element name="Table1">
							<xs:complexType>
								<xs:sequence>
									<xs:element name="RecordNumber" type="xs:int" minOccurs="0" />
									<xs:element name="RequestID" type="xs:long" minOccurs="0" />
									<xs:element name="RequestTypeID" type="xs:int" minOccurs="0" />
									<xs:element name="Date" type="xs:dateTime" minOccurs="0" />
									<xs:element name="Status" type="xs:string" minOccurs="0" />
									<xs:element name="PersonalAccount" type="xs:long" minOccurs="0" />
									<xs:element name="MSISDN" type="xs:string" minOccurs="0" />
									<xs:element name="ICCID" type="xs:string" minOccurs="0" />
									<xs:element name="Name" type="xs:string" minOccurs="0" />
									<xs:element name="OperatorId" type="xs:int" minOccurs="0" />
									<xs:element name="OperatorName" type="xs:string" minOccurs="0" />
									<xs:element name="ContractNr" type="xs:string" minOccurs="0" />
									<xs:element name="TDNr" type="xs:string" minOccurs="0" />
									<xs:element name="SalePointCode" type="xs:string" minOccurs="0" />
								</xs:sequence>
							</xs:complexType>
						</xs:element>
					</xs:choice>
				</xs:complexType>
			</xs:element>
		</xs:schema>
		<diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
			<NewDataSet xmlns="">
				<Table1 diffgr:id="Table11" msdata:rowOrder="0">
					<RecordNumber>1</RecordNumber>
					<RequestID>3000136132</RequestID>
					<RequestTypeID>140</RequestTypeID>
					<Date>2011-12-06T11:00:39+04:00</Date>
					<Status>zzzzzzzzz zzzzzzzzz</Status>
					<PersonalAccount>277300011803</PersonalAccount>
					<MSISDN>79171700134</MSISDN>
					<ICCID>89791010007886547620</ICCID>
					<Name>Testotico</Name>
					<OperatorId>9912</OperatorId>
					<OperatorName>zzzzzzzz1 zzz1</OperatorName>
					<ContractNr>8654762-0</ContractNr>
					<TDNr>377300042790</TDNr>
					<SalePointCode>123400320</SalePointCode>
				</Table1>
				<Table1 diffgr:id="Table12" msdata:rowOrder="1">
					<RecordNumber>2</RecordNumber>
					<RequestID>3000136128</RequestID>
					<RequestTypeID>140</RequestTypeID>
					<Date>2011-12-06T10:58:50+04:00</Date>
					<Status>zzzzzzzzz zzzzzzzzz</Status>
					<PersonalAccount>277300017817</PersonalAccount>
					<MSISDN>79120000116</MSISDN>
					<ICCID>89791010007767705306</ICCID>
					<Name>Testotico</Name>
					<OperatorId>9912</OperatorId>
					<OperatorName>zzzzzzzz1 zzz1</OperatorName>
					<ContractNr>6770530-6</ContractNr>
					<TDNr>377300051185</TDNr>
					<SalePointCode>123400320</SalePointCode>
				</Table1>
				<Table1 diffgr:id="Table13" msdata:rowOrder="2">
					<RecordNumber>3</RecordNumber>
					<RequestID>3000135790</RequestID>
					<RequestTypeID>140</RequestTypeID>
					<Date>2011-12-06T09:26:42+04:00</Date>
					<Status>zzzzzzzzz zzzzzzzzz</Status>
					<PersonalAccount>277300011799</PersonalAccount>
					<MSISDN>79171700129</MSISDN>
					<ICCID>89791010007886547584</ICCID>
					<Name>Tets Test Test</Name>
					<OperatorId>9912</OperatorId>
					<OperatorName>zzzzzzzz1 zzz1</OperatorName>
					<ContractNr>8654758-4</ContractNr>
					<TDNr>377300042786</TDNr>
					<SalePointCode>123400320</SalePointCode>
				</Table1>
			</NewDataSet>
		</diffgr:diffgram>
	</Reqs>
	<SalePointCode></SalePointCode>
	<Start>1</Start>
	<Status>-1</Status>
	<TDNr></TDNr>
	<TotalCount>3</TotalCount>
</RequestListDTO>] return value: [1]
=======================================""",
"""2011-12-07 09:05:23,758 [17] DEBUG FORIS.TelCRM.RemoteDealer.Services.Interfaces.IRequestDirectory
=======================================
[result] <ReceiveRegistrationRequests>  outputs parameters: [<?xml version="1.0" encoding="utf-16"?>
<RequestListDTO xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/FORIS.TelCRM.RemoteDealer.CommonLibrary">
	<ContractNr></ContractNr>
	<Count>20</Count>
	<CrmOperatorID>9912</CrmOperatorID>
	<CustomerFirstName></CustomerFirstName>
	<CustomerLastName></CustomerLastName>
	<CustomerMiddleName></CustomerMiddleName>
	<CustomerTypeID>-1</CustomerTypeID>
	<DateFrom>2011-12-06T09:04:54</DateFrom>
	<DateTo>2011-12-07T09:04:54</DateTo>
	<DealerID>6427</DealerID>
	<ForisOperatorID>-1003</ForisOperatorID>
	<ICCID></ICCID>
	<MSISDN></MSISDN>
	<OrganizationName></OrganizationName>
	<PA></PA>
	<ReqTypesAndPrivileges>
		<ReqTypePrivilege>
			<Privilege>ReceiveCustomerRegistrationDealerRequests</Privilege>
			<ReqType>CustomerRegistration</ReqType>
		</ReqTypePrivilege>
	</ReqTypesAndPrivileges>
	<Reqs>
		<xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
			<xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">
				<xs:complexType>
					<xs:choice minOccurs="0" maxOccurs="unbounded">
						<xs:element name="Table1">
							<xs:complexType>
								<xs:sequence>
									<xs:element name="RecordNumber" type="xs:int" minOccurs="0" />
									<xs:element name="RequestID" type="xs:long" minOccurs="0" />
									<xs:element name="RequestTypeID" type="xs:int" minOccurs="0" />
									<xs:element name="Date" type="xs:dateTime" minOccurs="0" />
									<xs:element name="Status" type="xs:string" minOccurs="0" />
									<xs:element name="PersonalAccount" type="xs:long" minOccurs="0" />
									<xs:element name="MSISDN" type="xs:string" minOccurs="0" />
									<xs:element name="ICCID" type="xs:string" minOccurs="0" />
									<xs:element name="Name" type="xs:string" minOccurs="0" />
									<xs:element name="OperatorId" type="xs:int" minOccurs="0" />
									<xs:element name="OperatorName" type="xs:string" minOccurs="0" />
									<xs:element name="ContractNr" type="xs:string" minOccurs="0" />
									<xs:element name="TDNr" type="xs:string" minOccurs="0" />
									<xs:element name="SalePointCode" type="xs:string" minOccurs="0" />
								</xs:sequence>
							</xs:complexType>
						</xs:element>
					</xs:choice>
				</xs:complexType>
			</xs:element>
		</xs:schema>
		<diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
			<NewDataSet xmlns="">
				<Table1 diffgr:id="Table11" msdata:rowOrder="0">
					<RecordNumber>1</RecordNumber>
					<RequestID>3000136132</RequestID>
					<RequestTypeID>140</RequestTypeID>
					<Date>2011-12-06T11:00:39+04:00</Date>
					<Status>zzzzzzzzz zzzzzzzzz</Status>
					<PersonalAccount>277300011803</PersonalAccount>
					<MSISDN>79171700134</MSISDN>
					<ICCID>89791010007886547620</ICCID>
					<Name>Testotico</Name>
					<OperatorId>9912</OperatorId>
					<OperatorName>zzzzzzzz1 zzz1</OperatorName>
					<ContractNr>8654762-0</ContractNr>
					<TDNr>377300042790</TDNr>
					<SalePointCode>123400320</SalePointCode>
				</Table1>
				<Table1 diffgr:id="Table12" msdata:rowOrder="1">
					<RecordNumber>2</RecordNumber>
					<RequestID>3000136128</RequestID>
					<RequestTypeID>140</RequestTypeID>
					<Date>2011-12-06T10:58:50+04:00</Date>
					<Status>zzzzzzzzz zzzzzzzzz</Status>
					<PersonalAccount>277300017817</PersonalAccount>
					<MSISDN>79120000116</MSISDN>
					<ICCID>89791010007767705306</ICCID>
					<Name>Testotico</Name>
					<OperatorId>9912</OperatorId>
					<OperatorName>zzzzzzzz1 zzz1</OperatorName>
					<ContractNr>6770530-6</ContractNr>
					<TDNr>377300051185</TDNr>
					<SalePointCode>123400320</SalePointCode>
				</Table1>
				<Table1 diffgr:id="Table13" msdata:rowOrder="2">
					<RecordNumber>3</RecordNumber>
					<RequestID>3000135790</RequestID>
					<RequestTypeID>140</RequestTypeID>
					<Date>2011-12-06T09:26:42+04:00</Date>
					<Status>zzzzzzzzz zzzzzzzzz</Status>
					<PersonalAccount>277300011799</PersonalAccount>
					<MSISDN>79171700129</MSISDN>
					<ICCID>89791010007886547584</ICCID>
					<Name>Tets Test Test</Name>
					<OperatorId>9912</OperatorId>
					<OperatorName>zzzzzzzz1 zzz1</OperatorName>
					<ContractNr>8654758-4</ContractNr>
					<TDNr>377300042786</TDNr>
					<SalePointCode>123400320</SalePointCode>
				</Table1>
			</NewDataSet>
		</diffgr:diffgram>
	</Reqs>
	<SalePointCode></SalePointCode>
	<Start>1</Start>
	<Status>-1</Status>
	<TDNr></TDNr>
	<TotalCount>3</TotalCount>
</RequestListDTO>] return value: [1]
======================================="""),

("""2011-12-07 09:08:19,978 [17] DEBUG
=======================================
GetMessages [request]:<?xml version="1.0" encoding="utf-16"?><PlatformActivationMessagesRequest xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001"><Actions><ParameterizedAction><Action xmlns:d4p1="http://schemas.sitels.ru/Marti.OrderCatalogue.Contracts/v001"><d4p1:ActionTypeCode>Delete</d4p1:ActionTypeCode><d4p1:BasketAction>Add</d4p1:BasketAction><d4p1:CustomAttributes i:nil="true" /><d4p1:ProductIdentifier><d4p1:CustomAttributes i:nil="true" /><d4p1:ExternalPackageId>10</d4p1:ExternalPackageId><d4p1:ExternalPackageTypeCode i:nil="true" /><d4p1:ExternalProductCode>FRBLKINIT</d4p1:ExternalProductCode><d4p1:ExternalProductId>1</d4p1:ExternalProductId><d4p1:ExternalProductType i:nil="true" /><d4p1:OrderTypeCode>PRODUCT_SERVICE</d4p1:OrderTypeCode><d4p1:PackageId i:nil="true" /><d4p1:PackageVersionDate i:nil="true" /><d4p1:ProductCode>PRODUCT_SERVICE#FRBLKINIT</d4p1:ProductCode><d4p1:ProductId>10094</d4p1:ProductId><d4p1:ProductStatus i:nil="true" /><d4p1:ProductVersionDate>2011-10-24T14:13:57</d4p1:ProductVersionDate><d4p1:ProductVersionId i:nil="true" /><d4p1:SubOrderTypeCode>Blocking</d4p1:SubOrderTypeCode></d4p1:ProductIdentifier><d4p1:AttributesRequest /><d4p1:IsRelation>false</d4p1:IsRelation><d4p1:Quantity>1</d4p1:Quantity><d4p1:Children /><d4p1:ActionDate i:nil="true" /><d4p1:CustomActionDate i:nil="true" /></Action><Parameters xmlns:d4p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays"><d4p1:KeyValueOfstringstring><d4p1:Key>DoNotProcessingInFinancialPlatform</d4p1:Key><d4p1:Value>False</d4p1:Value></d4p1:KeyValueOfstringstring></Parameters></ParameterizedAction></Actions><Identity><PersonalAccountNumber>277300016621</PersonalAccountNumber><PhoneNumber>79171590570</PhoneNumber><Imsi i:nil="true" /></Identity><Options>None</Options><Parameters xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" i:nil="true" /><RequestUser><UserId i:nil="true" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001" /><UserNtName xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001">NT AUTHORITY\SYSTEM</UserNtName><MsisdnInitiator i:nil="true" /><UserHostAddress i:nil="true" /></RequestUser><SourceSystem>CRM.OM</SourceSystem></PlatformActivationMessagesRequest>
=======================================""",
"""2011-12-07 09:08:19,978 [17] DEBUG
=======================================
GetMessages [request]:<?xml version="1.0" encoding="utf-16"?>
<PlatformActivationMessagesRequest xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001">
    <Actions>
        <ParameterizedAction>
            <Action xmlns:d4p1="http://schemas.sitels.ru/Marti.OrderCatalogue.Contracts/v001">
                <d4p1:ActionTypeCode>Delete</d4p1:ActionTypeCode>
                <d4p1:BasketAction>Add</d4p1:BasketAction>
                <d4p1:CustomAttributes i:nil="true" />
                <d4p1:ProductIdentifier>
                    <d4p1:CustomAttributes i:nil="true" />
                    <d4p1:ExternalPackageId>10</d4p1:ExternalPackageId>
                    <d4p1:ExternalPackageTypeCode i:nil="true" />
                    <d4p1:ExternalProductCode>FRBLKINIT</d4p1:ExternalProductCode>
                    <d4p1:ExternalProductId>1</d4p1:ExternalProductId>
                    <d4p1:ExternalProductType i:nil="true" />
                    <d4p1:OrderTypeCode>PRODUCT_SERVICE</d4p1:OrderTypeCode>
                    <d4p1:PackageId i:nil="true" />
                    <d4p1:PackageVersionDate i:nil="true" />
                    <d4p1:ProductCode>PRODUCT_SERVICE#FRBLKINIT</d4p1:ProductCode>
                    <d4p1:ProductId>10094</d4p1:ProductId>
                    <d4p1:ProductStatus i:nil="true" />
                    <d4p1:ProductVersionDate>2011-10-24T14:13:57</d4p1:ProductVersionDate>
                    <d4p1:ProductVersionId i:nil="true" />
                    <d4p1:SubOrderTypeCode>Blocking</d4p1:SubOrderTypeCode>
                </d4p1:ProductIdentifier>
                <d4p1:AttributesRequest />
                <d4p1:IsRelation>false</d4p1:IsRelation>
                <d4p1:Quantity>1</d4p1:Quantity>
                <d4p1:Children />
                <d4p1:ActionDate i:nil="true" />
                <d4p1:CustomActionDate i:nil="true" />
            </Action>
            <Parameters xmlns:d4p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
                <d4p1:KeyValueOfstringstring>
                    <d4p1:Key>DoNotProcessingInFinancialPlatform</d4p1:Key>
                    <d4p1:Value>False</d4p1:Value>
                </d4p1:KeyValueOfstringstring>
            </Parameters>
        </ParameterizedAction>
    </Actions>
    <Identity>
        <PersonalAccountNumber>277300016621</PersonalAccountNumber>
        <PhoneNumber>79171590570</PhoneNumber>
        <Imsi i:nil="true" />
    </Identity>
    <Options>None</Options>
    <Parameters xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" i:nil="true" />
    <RequestUser>
        <UserId i:nil="true" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001" />
        <UserNtName xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001">NT AUTHORITY\SYSTEM</UserNtName>
        <MsisdnInitiator i:nil="true" />
        <UserHostAddress i:nil="true" />
    </RequestUser>
    <SourceSystem>CRM.OM</SourceSystem>
</PlatformActivationMessagesRequest>
======================================="""),

("""[2011-12-07 09:08:24,541] (DEBUG) 54 - ValidationUnit [result] <GetUserInfoByName>  outputs parameters: [] return value: [<?xml version="1.0" encoding="utf-16"?>
<ForisSecurityUserInfo xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sts.sitronics.com/Foris/TelCrm/CustomerManagement/v1/Dto">
	<Birthday i:nil="true" />
	<DomainName>sts</DomainName>
	<FirstName>Sabina</FirstName>
	<FullLogin>sts\smovsesyan</FullLogin>
	<FullName>zzzzzzzz zzzzzz zzzzzzzzzzz</FullName>
	<Id>10033056</Id>
	<IsBlocked>false</IsBlocked>
	<LastName>Movsesyan</LastName>
	<Login>smovsesyan</Login>
	<PatName></PatName>
</ForisSecurityUserInfo>]""",
"""[2011-12-07 09:08:24,541] (DEBUG) 54 - ValidationUnit [result] <GetUserInfoByName>  outputs parameters: [] return value: [<?xml version="1.0" encoding="utf-16"?>
<ForisSecurityUserInfo xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sts.sitronics.com/Foris/TelCrm/CustomerManagement/v1/Dto">
	<Birthday i:nil="true" />
	<DomainName>sts</DomainName>
	<FirstName>Sabina</FirstName>
	<FullLogin>sts\smovsesyan</FullLogin>
	<FullName>zzzzzzzz zzzzzz zzzzzzzzzzz</FullName>
	<Id>10033056</Id>
	<IsBlocked>false</IsBlocked>
	<LastName>Movsesyan</LastName>
	<Login>smovsesyan</Login>
	<PatName></PatName>
</ForisSecurityUserInfo>]"""),
("""2011-12-07 09:08:42,294 [16] DEBUG FORIS.TelCRM.RemoteDealer.Services.Interfaces.Behaviors.ContextFlowBehaviorAttribute
=======================================
OperationInfo = <?xml version="1.0" encoding="utf-16"?><ContextOperationInfo xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/FORIS.TelCRM.RemoteDealer.CommonLibrary.Context"><BpCode>SalesContract</BpCode><SourceType>RemoteDealer</SourceType></ContextOperationInfo>
OperatorInfo = <?xml version="1.0" encoding="utf-16"?><ContextOperatorInfo xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/FORIS.TelCRM.RemoteDealer.CommonLibrary.Context"><ForisOperatorId>-1003</ForisOperatorId><FullLogin>6427\-1003</FullLogin><OperatorName>zzzzzzzz Test1</OperatorName><RequestUrl>/salesui/ContractRegistration.aspx</RequestUrl><UserHostAddress>172.25.29.80</UserHostAddress></ContextOperatorInfo>
=======================================""",
"""2011-12-07 09:08:42,294 [16] DEBUG FORIS.TelCRM.RemoteDealer.Services.Interfaces.Behaviors.ContextFlowBehaviorAttribute
=======================================
OperationInfo = <?xml version="1.0" encoding="utf-16"?>
<ContextOperationInfo xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/FORIS.TelCRM.RemoteDealer.CommonLibrary.Context">
    <BpCode>SalesContract</BpCode>
    <SourceType>RemoteDealer</SourceType>
</ContextOperationInfo>

OperatorInfo = <?xml version="1.0" encoding="utf-16"?>
<ContextOperatorInfo xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/FORIS.TelCRM.RemoteDealer.CommonLibrary.Context">
    <ForisOperatorId>-1003</ForisOperatorId>
    <FullLogin>6427\-1003</FullLogin>
    <OperatorName>zzzzzzzz Test1</OperatorName>
    <RequestUrl>/salesui/ContractRegistration.aspx</RequestUrl>
    <UserHostAddress>172.25.29.80</UserHostAddress>
</ContextOperatorInfo>
======================================="""),

("""2011-12-07 09:08:42,888 [16] DEBUG FORIS.TelCRM.RemoteDealer.DomainModel.Directories.GetCustomizationDirectory
=======================================
Read customization configuration: <ConfigurationInstance Place="MTS"><!-- zzzzzzzzz zzzzzzzzz z zzzzzzzzzzzzzz zzzzz.--><Fields><!--zzzzz zzzzzzzz.--><Field Name="BirthdayPlace" isRequired="true" isVisible="true" /><!--zzz.--><Field Name="KPP" isRequired="true" isVisible="true" /><!--zzzzzzzzzzzzzz zzzzz zzzzzzzz.--><Field Name="AdditionalBillDelivery" isRequired="true" isVisible="true" /><!--zzzzz.--><Field Name="AdvancePayment" isRequired="true" isVisible="true" /><!--zzzzzzz zzzzz.--><Field Name="CodeWord" isRequired="true" isVisible="true" /><!--zzzz zzzzzzzzz zzzzzzzzzzz.--><Field Name="TempAddressDateTo" isRequired="true" isVisible="true" /><!--zzzzzzzzzzz zzzzc zzzzzzzzzzz.--><Field Name="OrgFactAddress" isRequired="true" isVisible="true" /><!--zzzzzz.--><Field Name="Region" isRequired="false" isVisible="false" /><!-- zzzz zzzzzzzz zzzzzzzzz.--><Field Name="IdentificationValidPeriod" isRequired="false" isVisible="false" /></Fields><!-- zzzzzzzzz.--><Settings><!-- zzzzzzzzz zzzzzz zzzzzzzzz --><Setting Name="IsSyncCreateRequest" Value="true" /><!--zzzzzzzzzzzzz zzz zzzzzzzzz zzzzzz zzzzzzzzz.--><Setting Name="ReservAllPhones" Value="false" /><!--zzzzzzzzzz zzzzzzz zzzzzz.--><Setting Name="FavoriteNumbersView" Value="false" /><!--zzzzzzzzzzzzz zzz zzzzzzzzz zzzzzz zzzzzzzzz.--><Setting Name="VisibleCustomerTypeLC" Value="1,2,3" /><!-- zzzz zzz zzzzz zzzzzzzzzz --><Setting Name="DocumentTypeCodes" Value="DetailedBalanceReport,CallDetailsByPeriod,Bill,PreBill,CallDetailsByBill" /><!--zzzzz zzzzzzzz zzzzzz zzzzzzzz.--><Setting Name="PrefixPhoneNumberLength" Value="1" /><!-- zzzzzzzzzzzzz zzzzzzzzzzzzzzz. --><Setting Name="VisibleIndividualEntrepreneurForm" Value="true" /><!-- zzzz zzzzzzzz zzzzzzzzz.--><Setting Name="CheckIdentificationValidity" Value="false" /><!-- zzzzzzzz zzz zzzzzzzzzz zzzzz zz zzzz zzzzzzz.--><Setting Name="GetNetworkOperatorCodeByRegionCode" Value="false" /><!-- zzzzzzz zzzzzzzz zzzzzzzz zzzzzzzzzz zzzzzz zzz z zzzzzz zzzzzzzz.--><Setting Name="SkipPhoneAndIccidHostVerificaion" Value="false" /><!--zzzzzzzz zzzzz zzzzzz zzzzzz zzzzzzzz zzz zzzzzzzzz zzzzzzzzzzzzz.--><Setting Name="SimNumberLengthForContract" Value="8" /><Setting Name="JeansTariffPlanGroup" Value="Jeans" /><!-- zzzzz zzzzz zzzzzzzz --><Setting Name="PassportSeriesLength" Value="4" /><!-- zzzzz zzzzzz zzzzzzzz --><Setting Name="PassportNumberLength" Value="6" /><!-- zzzzzzzzzzz zzzzzzzz. zzzzz zzzzzzzz zzzzzzzzzzzzzz, zzzz zzzzzzz zzzzzz 14 zzz 18 zzz --><Setting Name="AgeRestrictionWarning" Value="14,18" /><!-- zzzzzzzzzzz zzzzzzzz. zzzzzzzzzzz zzzzzz zzzzz zzzzzzzzz, zzzz zzzzzzz zzzzzzzz zzzzzz 18 zzz --><Setting Name="AgeRestrictionError" Value="18" /></Settings><!-- zzzzzz-zzzzzzzz.--><BusinessProcesses><BusinessProcess Name="SalesContract"><SaleSourceTypes><SaleSourceType Name="RemoteDealer"><Settings><!--zzzzzzzz zzzzz zzzzzz zzzzzz zzzzzzzz zzz zzzzzzzzz zzzzzzzzzzzzz.--><Setting Name="HidePhoneMaskSalabilities" Value="E" /></Settings></SaleSourceType></SaleSourceTypes></BusinessProcess><BusinessProcess Name="ActivationComplect"><Settings><Setting Name="UseNewRequest" Value="true" /></Settings></BusinessProcess><BusinessProcess Name="ChangePresentOwner"><Settings><!-- zzzzzzzzzzzz zzzzz zzzzzzzz zzzzzzzzzzz zzzzzz --><Setting Name="UseNewRequest" Value="true" /><Setting Name="IsSyncCreateRequest" Value="true" /></Settings></BusinessProcess><BusinessProcess Name="SaleComplect"><Settings><!-- zzzzzzzzzzzz zzzzz zzzzzzzz zzzzzzzzzzz zzzzzz --><Setting Name="UseNewRequest" Value="false" /><Setting Name="IsSyncCreateRequest" Value="true" /></Settings></BusinessProcess><BusinessProcess Name="ChangeSIM"><Settings><!-- zzzzzzzzzzzz zzzzz zzzzzzzz zzzzzzzzzzz zzzzzz --><Setting Name="UseNewRequest" Value="true" /></Settings></BusinessProcess></BusinessProcesses></ConfigurationInstance>
=======================================""",
"""2011-12-07 09:08:42,888 [16] DEBUG FORIS.TelCRM.RemoteDealer.DomainModel.Directories.GetCustomizationDirectory
=======================================
Read customization configuration: <ConfigurationInstance Place="MTS">
    <!-- zzzzzzzzz zzzzzzzzz z zzzzzzzzzzzzzz zzzzz.-->
    <Fields>
        <!--zzzzz zzzzzzzz.-->
        <Field Name="BirthdayPlace" isRequired="true" isVisible="true" />
        <!--zzz.-->
        <Field Name="KPP" isRequired="true" isVisible="true" />
        <!--zzzzzzzzzzzzzz zzzzz zzzzzzzz.-->
        <Field Name="AdditionalBillDelivery" isRequired="true" isVisible="true" />
        <!--zzzzz.-->
        <Field Name="AdvancePayment" isRequired="true" isVisible="true" />
        <!--zzzzzzz zzzzz.-->
        <Field Name="CodeWord" isRequired="true" isVisible="true" />
        <!--zzzz zzzzzzzzz zzzzzzzzzzz.-->
        <Field Name="TempAddressDateTo" isRequired="true" isVisible="true" />
        <!--zzzzzzzzzzz zzzzc zzzzzzzzzzz.-->
        <Field Name="OrgFactAddress" isRequired="true" isVisible="true" />
        <!--zzzzzz.-->
        <Field Name="Region" isRequired="false" isVisible="false" />
        <!-- zzzz zzzzzzzz zzzzzzzzz.-->
        <Field Name="IdentificationValidPeriod" isRequired="false" isVisible="false" />
    </Fields>
    <!-- zzzzzzzzz.-->
    <Settings>
        <!-- zzzzzzzzz zzzzzz zzzzzzzzz -->
        <Setting Name="IsSyncCreateRequest" Value="true" />
        <!--zzzzzzzzzzzzz zzz zzzzzzzzz zzzzzz zzzzzzzzz.-->
        <Setting Name="ReservAllPhones" Value="false" />
        <!--zzzzzzzzzz zzzzzzz zzzzzz.-->
        <Setting Name="FavoriteNumbersView" Value="false" />
        <!--zzzzzzzzzzzzz zzz zzzzzzzzz zzzzzz zzzzzzzzz.-->
        <Setting Name="VisibleCustomerTypeLC" Value="1,2,3" />
        <!-- zzzz zzz zzzzz zzzzzzzzzz -->
        <Setting Name="DocumentTypeCodes" Value="DetailedBalanceReport,CallDetailsByPeriod,Bill,PreBill,CallDetailsByBill" />
        <!--zzzzz zzzzzzzz zzzzzz zzzzzzzz.-->
        <Setting Name="PrefixPhoneNumberLength" Value="1" />
        <!-- zzzzzzzzzzzzz zzzzzzzzzzzzzzz. -->
        <Setting Name="VisibleIndividualEntrepreneurForm" Value="true" />
        <!-- zzzz zzzzzzzz zzzzzzzzz.-->
        <Setting Name="CheckIdentificationValidity" Value="false" />
        <!-- zzzzzzzz zzz zzzzzzzzzz zzzzz zz zzzz zzzzzzz.-->
        <Setting Name="GetNetworkOperatorCodeByRegionCode" Value="false" />
        <!-- zzzzzzz zzzzzzzz zzzzzzzz zzzzzzzzzz zzzzzz zzz z zzzzzz zzzzzzzz.-->
        <Setting Name="SkipPhoneAndIccidHostVerificaion" Value="false" />
        <!--zzzzzzzz zzzzz zzzzzz zzzzzz zzzzzzzz zzz zzzzzzzzz zzzzzzzzzzzzz.-->
        <Setting Name="SimNumberLengthForContract" Value="8" />
        <Setting Name="JeansTariffPlanGroup" Value="Jeans" />
        <!-- zzzzz zzzzz zzzzzzzz -->
        <Setting Name="PassportSeriesLength" Value="4" />
        <!-- zzzzz zzzzzz zzzzzzzz -->
        <Setting Name="PassportNumberLength" Value="6" />
        <!-- zzzzzzzzzzz zzzzzzzz. zzzzz zzzzzzzz zzzzzzzzzzzzzz, zzzz zzzzzzz zzzzzz 14 zzz 18 zzz -->
        <Setting Name="AgeRestrictionWarning" Value="14,18" />
        <!-- zzzzzzzzzzz zzzzzzzz. zzzzzzzzzzz zzzzzz zzzzz zzzzzzzzz, zzzz zzzzzzz zzzzzzzz zzzzzz 18 zzz -->
        <Setting Name="AgeRestrictionError" Value="18" />
    </Settings>
    <!-- zzzzzz-zzzzzzzz.-->
    <BusinessProcesses>
        <BusinessProcess Name="SalesContract">
            <SaleSourceTypes>
                <SaleSourceType Name="RemoteDealer">
                    <Settings>
                        <!--zzzzzzzz zzzzz zzzzzz zzzzzz zzzzzzzz zzz zzzzzzzzz zzzzzzzzzzzzz.-->
                        <Setting Name="HidePhoneMaskSalabilities" Value="E" />
                    </Settings>
                </SaleSourceType>
            </SaleSourceTypes>
        </BusinessProcess>
        <BusinessProcess Name="ActivationComplect">
            <Settings>
                <Setting Name="UseNewRequest" Value="true" />
            </Settings>
        </BusinessProcess>
        <BusinessProcess Name="ChangePresentOwner">
            <Settings>
                <!-- zzzzzzzzzzzz zzzzz zzzzzzzz zzzzzzzzzzz zzzzzz -->
                <Setting Name="UseNewRequest" Value="true" />
                <Setting Name="IsSyncCreateRequest" Value="true" />
            </Settings>
        </BusinessProcess>
        <BusinessProcess Name="SaleComplect">
            <Settings>
                <!-- zzzzzzzzzzzz zzzzz zzzzzzzz zzzzzzzzzzz zzzzzz -->
                <Setting Name="UseNewRequest" Value="false" />
                <Setting Name="IsSyncCreateRequest" Value="true" />
            </Settings>
        </BusinessProcess>
        <BusinessProcess Name="ChangeSIM">
            <Settings>
                <!-- zzzzzzzzzzzz zzzzz zzzzzzzz zzzzzzzzzzz zzzzzz -->
                <Setting Name="UseNewRequest" Value="true" />
            </Settings>
        </BusinessProcess>
    </BusinessProcesses>
</ConfigurationInstance>
======================================="""),
("""2011-12-07 09:09:20,933 [16] DEBUG OrderManagement.BusinessProcess.API.TerminalDevice.TerminalDeviceService
---------------------------------------
[call] <ChangeProducts>  call parameters: [<?xml version="1.0" encoding="utf-16"?>
<ChangeProductsRequest xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001">
	<Comment i:nil="true" />
	<ExternalRequestInitiatorId i:nil="true" />
	<ExternalRequestInitiatorType>Unknown</ExternalRequestInitiatorType>
	<ExternalSerializeObject i:nil="true" />
	<ParentRequestId>3000137460</ParentRequestId>
	<ParentRequestTypeCode i:nil="true" />
	<RequestUser>
		<UserId xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001">1</UserId>
		<UserNtName i:nil="true" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001" />
		<MsisdnInitiator i:nil="true" />
		<UserHostAddress i:nil="true" />
	</RequestUser>
	<SalePointCode></SalePointCode>
	<SourceType>Office</SourceType>
	<AutomaticCompensation xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
		<d2p1:string>ADD_CUSTOMER_FORBIDDEN</d2p1:string>
		<d2p1:string>ACTION_REQUIRED</d2p1:string>
		<d2p1:string>REMOVE_REQUIRED</d2p1:string>
		<d2p1:string>ADD_DATE</d2p1:string>
		<d2p1:string>CHANGE_DATE</d2p1:string>
		<d2p1:string>ACTION_DATE</d2p1:string>
		<d2p1:string>ADD_REQUIRED</d2p1:string>
		<d2p1:string>ADD_NOT_ALLOWED</d2p1:string>
	</AutomaticCompensation>
	<ChildRequests i:nil="true" />
	<ExecuteFlags i:nil="true" />
	<LanguageCode i:nil="true" />
	<MakeInvoice i:nil="true" />
	<ParentRequestTypeId i:nil="true" />
	<PhoneNumber>79169000091</PhoneNumber>
	<ProductActions xmlns:d2p1="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001">
		<d2p1:ProductActionBase i:type="d2p1:ServiceAction">
			<d2p1:ActionDate i:nil="true" />
			<d2p1:ActionType>Add</d2p1:ActionType>
			<d2p1:ChildActions i:nil="true" />
			<d2p1:IsRelation>false</d2p1:IsRelation>
			<d2p1:NeedTariffication>false</d2p1:NeedTariffication>
			<d2p1:OTPrice i:nil="true" />
			<d2p1:Parameters i:nil="true" />
			<d2p1:ParentPackageId i:nil="true" />
			<d2p1:Product i:nil="true" />
			<d2p1:BonusCampaignId i:nil="true" />
			<d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
			<d2p1:IsAutomaticAdded i:nil="true" />
			<d2p1:NeedCheckBlocks i:nil="true" />
			<d2p1:Quantity i:nil="true" />
			<d2p1:ServiceId>
				<d2p1:ServiceCode i:nil="true" />
				<d2p1:ServiceId>24</d2p1:ServiceId>
			</d2p1:ServiceId>
			<d2p1:ServiceName i:nil="true" />
			<d2p1:TariffPlanId i:nil="true" />
		</d2p1:ProductActionBase>
		<d2p1:ProductActionBase i:type="d2p1:ServiceAction">
			<d2p1:ActionDate i:nil="true" />
			<d2p1:ActionType>Add</d2p1:ActionType>
			<d2p1:ChildActions i:nil="true" />
			<d2p1:IsRelation>false</d2p1:IsRelation>
			<d2p1:NeedTariffication>false</d2p1:NeedTariffication>
			<d2p1:OTPrice i:nil="true" />
			<d2p1:Parameters i:nil="true" />
			<d2p1:ParentPackageId i:nil="true" />
			<d2p1:Product i:nil="true" />
			<d2p1:BonusCampaignId i:nil="true" />
			<d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
			<d2p1:IsAutomaticAdded i:nil="true" />
			<d2p1:NeedCheckBlocks i:nil="true" />
			<d2p1:Quantity i:nil="true" />
			<d2p1:ServiceId>
				<d2p1:ServiceCode i:nil="true" />
				<d2p1:ServiceId>6550</d2p1:ServiceId>
			</d2p1:ServiceId>
			<d2p1:ServiceName i:nil="true" />
			<d2p1:TariffPlanId i:nil="true" />
		</d2p1:ProductActionBase>
	</ProductActions>
	<RegisterId i:nil="true" />
	<SkipValidation>false</SkipValidation>
	<UseOcf>false</UseOcf>
	<UserConfirmationResult>false</UserConfirmationResult>
</ChangeProductsRequest>]
---------------------------------------""",
"""2011-12-07 09:09:20,933 [16] DEBUG OrderManagement.BusinessProcess.API.TerminalDevice.TerminalDeviceService
---------------------------------------
[call] <ChangeProducts>  call parameters: [<?xml version="1.0" encoding="utf-16"?>
<ChangeProductsRequest xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001">
	<Comment i:nil="true" />
	<ExternalRequestInitiatorId i:nil="true" />
	<ExternalRequestInitiatorType>Unknown</ExternalRequestInitiatorType>
	<ExternalSerializeObject i:nil="true" />
	<ParentRequestId>3000137460</ParentRequestId>
	<ParentRequestTypeCode i:nil="true" />
	<RequestUser>
		<UserId xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001">1</UserId>
		<UserNtName i:nil="true" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001" />
		<MsisdnInitiator i:nil="true" />
		<UserHostAddress i:nil="true" />
	</RequestUser>
	<SalePointCode></SalePointCode>
	<SourceType>Office</SourceType>
	<AutomaticCompensation xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
		<d2p1:string>ADD_CUSTOMER_FORBIDDEN</d2p1:string>
		<d2p1:string>ACTION_REQUIRED</d2p1:string>
		<d2p1:string>REMOVE_REQUIRED</d2p1:string>
		<d2p1:string>ADD_DATE</d2p1:string>
		<d2p1:string>CHANGE_DATE</d2p1:string>
		<d2p1:string>ACTION_DATE</d2p1:string>
		<d2p1:string>ADD_REQUIRED</d2p1:string>
		<d2p1:string>ADD_NOT_ALLOWED</d2p1:string>
	</AutomaticCompensation>
	<ChildRequests i:nil="true" />
	<ExecuteFlags i:nil="true" />
	<LanguageCode i:nil="true" />
	<MakeInvoice i:nil="true" />
	<ParentRequestTypeId i:nil="true" />
	<PhoneNumber>79169000091</PhoneNumber>
	<ProductActions xmlns:d2p1="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001">
		<d2p1:ProductActionBase i:type="d2p1:ServiceAction">
			<d2p1:ActionDate i:nil="true" />
			<d2p1:ActionType>Add</d2p1:ActionType>
			<d2p1:ChildActions i:nil="true" />
			<d2p1:IsRelation>false</d2p1:IsRelation>
			<d2p1:NeedTariffication>false</d2p1:NeedTariffication>
			<d2p1:OTPrice i:nil="true" />
			<d2p1:Parameters i:nil="true" />
			<d2p1:ParentPackageId i:nil="true" />
			<d2p1:Product i:nil="true" />
			<d2p1:BonusCampaignId i:nil="true" />
			<d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
			<d2p1:IsAutomaticAdded i:nil="true" />
			<d2p1:NeedCheckBlocks i:nil="true" />
			<d2p1:Quantity i:nil="true" />
			<d2p1:ServiceId>
				<d2p1:ServiceCode i:nil="true" />
				<d2p1:ServiceId>24</d2p1:ServiceId>
			</d2p1:ServiceId>
			<d2p1:ServiceName i:nil="true" />
			<d2p1:TariffPlanId i:nil="true" />
		</d2p1:ProductActionBase>
		<d2p1:ProductActionBase i:type="d2p1:ServiceAction">
			<d2p1:ActionDate i:nil="true" />
			<d2p1:ActionType>Add</d2p1:ActionType>
			<d2p1:ChildActions i:nil="true" />
			<d2p1:IsRelation>false</d2p1:IsRelation>
			<d2p1:NeedTariffication>false</d2p1:NeedTariffication>
			<d2p1:OTPrice i:nil="true" />
			<d2p1:Parameters i:nil="true" />
			<d2p1:ParentPackageId i:nil="true" />
			<d2p1:Product i:nil="true" />
			<d2p1:BonusCampaignId i:nil="true" />
			<d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
			<d2p1:IsAutomaticAdded i:nil="true" />
			<d2p1:NeedCheckBlocks i:nil="true" />
			<d2p1:Quantity i:nil="true" />
			<d2p1:ServiceId>
				<d2p1:ServiceCode i:nil="true" />
				<d2p1:ServiceId>6550</d2p1:ServiceId>
			</d2p1:ServiceId>
			<d2p1:ServiceName i:nil="true" />
			<d2p1:TariffPlanId i:nil="true" />
		</d2p1:ProductActionBase>
	</ProductActions>
	<RegisterId i:nil="true" />
	<SkipValidation>false</SkipValidation>
	<UseOcf>false</UseOcf>
	<UserConfirmationResult>false</UserConfirmationResult>
</ChangeProductsRequest>]
---------------------------------------"""),
("""[13:07:04.8158468][thread 9] \t\tSaving attribute: attId=1683, dataTypeId=tpLongText, table_row_id=, value=<?xml version="1.0" encoding="utf-16"?><ProductsContainer xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001"><Actions xmlns:d2p1="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001"><d2p1:ProductActionBase i:type="d2p1:TariffPlanAction"><d2p1:ActionDate i:nil="true" /><d2p1:ActionType>Delete</d2p1:ActionType><d2p1:ChildActions /><d2p1:IsRelation>false</d2p1:IsRelation><d2p1:NeedTariffication>true</d2p1:NeedTariffication><d2p1:OTPrice i:nil="true" /><d2p1:Parameters /><d2p1:ParentPackageId i:nil="true" /><d2p1:Product><d2p1:ChildProducts i:nil="true" /><d2p1:PEPrice i:nil="true" /><d2p1:ProductId><d2p1:ExternalPackageId i:nil="true" /><d2p1:ExternalProductCode>11</d2p1:ExternalProductCode><d2p1:ExternalProductId>11</d2p1:ExternalProductId><d2p1:PackageId i:nil="true" /><d2p1:ProductCode>TariffPlan#11</d2p1:ProductCode><d2p1:ProductId>9952</d2p1:ProductId><d2p1:VersionDate>2011-10-27T11:42:10</d2p1:VersionDate><d2p1:VersionId>242123</d2p1:VersionId></d2p1:ProductId><d2p1:ProductLocal><d2p1:ProductLocal><d2p1:Description i:nil="true" /><d2p1:Info i:nil="true" /><d2p1:LanguageCode>1</d2p1:LanguageCode><d2p1:Name>zzz zzzzzz - zzzzzz 200</d2p1:Name><d2p1:VersionDate>2011-10-27T11:42:10</d2p1:VersionDate></d2p1:ProductLocal></d2p1:ProductLocal><d2p1:ProductType>TariffPlan</d2p1:ProductType><d2p1:SubOrderTypeCode i:nil="true" /></d2p1:Product><d2p1:TariffPlanCode i:nil="true" /><d2p1:TariffPlanId>11</d2p1:TariffPlanId></d2p1:ProductActionBase><d2p1:ProductActionBase i:type="d2p1:TariffPlanAction"><d2p1:ActionDate i:nil="true" /><d2p1:ActionType>Add</d2p1:ActionType><d2p1:ChildActions /><d2p1:IsRelation>false</d2p1:IsRelation><d2p1:NeedTariffication>true</d2p1:NeedTariffication><d2p1:OTPrice><d2p1:BasicPrice>50</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>59.00</d2p1:Price><d2p1:ServiceCode>FRCHB</d2p1:ServiceCode><d2p1:ServiceId>4260</d2p1:ServiceId><d2p1:ServiceName>zzzzz zzzzzzzzz zzzzz zz zzzzz zzzzzzz zz</d2p1:ServiceName><d2p1:Tax>9.00</d2p1:Tax></d2p1:OTPrice><d2p1:Parameters><d2p1:ProductActionParameter><d2p1:Code>NewCalculationMethodAlgorithm</d2p1:Code><d2p1:Value>Profile</d2p1:Value></d2p1:ProductActionParameter><d2p1:ProductActionParameter><d2p1:Code>NewTrustCategoryAlgorithm</d2p1:Code><d2p1:Value>Recommended</d2p1:Value></d2p1:ProductActionParameter><d2p1:ProductActionParameter><d2p1:Code>NewMarketingCategoryAlgorithm</d2p1:Code><d2p1:Value>NotChange</d2p1:Value></d2p1:ProductActionParameter><d2p1:ProductActionParameter><d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code><d2p1:Value>0</d2p1:Value></d2p1:ProductActionParameter></d2p1:Parameters><d2p1:ParentPackageId i:nil="true" /><d2p1:Product><d2p1:ChildProducts i:nil="true" /><d2p1:PEPrice i:nil="true" /><d2p1:ProductId><d2p1:ExternalPackageId i:nil="true" /><d2p1:ExternalProductCode>10</d2p1:ExternalProductCode><d2p1:ExternalProductId>10</d2p1:ExternalProductId><d2p1:PackageId i:nil="true" /><d2p1:ProductCode>TariffPlan#10</d2p1:ProductCode><d2p1:ProductId>9951</d2p1:ProductId><d2p1:VersionDate>2011-10-03T14:26:04</d2p1:VersionDate><d2p1:VersionId>141944</d2p1:VersionId></d2p1:ProductId><d2p1:ProductLocal><d2p1:ProductLocal><d2p1:Description i:nil="true" /><d2p1:Info i:nil="true" /><d2p1:LanguageCode>1</d2p1:LanguageCode><d2p1:Name>zzz zzzzzz - zzzzzz 100</d2p1:Name><d2p1:VersionDate>2011-10-03T14:26:04</d2p1:VersionDate></d2p1:ProductLocal></d2p1:ProductLocal><d2p1:ProductType>TariffPlan</d2p1:ProductType><d2p1:SubOrderTypeCode i:nil="true" /></d2p1:Product><d2p1:TariffPlanCode>10</d2p1:TariffPlanCode><d2p1:TariffPlanId>10</d2p1:TariffPlanId></d2p1:ProductActionBase><d2p1:ProductActionBase i:type="d2p1:ContextProductAction"><d2p1:ActionDate i:nil="true" /><d2p1:ActionType>Modify</d2p1:ActionType><d2p1:ChildActions /><d2p1:IsRelation>false</d2p1:IsRelation><d2p1:NeedTariffication>true</d2p1:NeedTariffication><d2p1:OTPrice i:nil="true" /><d2p1:Parameters /><d2p1:ParentPackageId i:nil="true" /><d2p1:Product><d2p1:ChildProducts i:nil="true" /><d2p1:PEPrice i:nil="true" /><d2p1:ProductId><d2p1:ExternalPackageId i:nil="true" /><d2p1:ExternalProductCode i:nil="true" /><d2p1:ExternalProductId i:nil="true" /><d2p1:PackageId i:nil="true" /><d2p1:ProductCode>Contract</d2p1:ProductCode><d2p1:ProductId>10698</d2p1:ProductId><d2p1:VersionDate>0100-01-01T00:00:00</d2p1:VersionDate><d2p1:VersionId>11219</d2p1:VersionId></d2p1:ProductId><d2p1:ProductLocal><d2p1:ProductLocal><d2p1:Description i:nil="true" /><d2p1:Info i:nil="true" /><d2p1:LanguageCode>1</d2p1:LanguageCode><d2p1:Name>zzzzzzzz</d2p1:Name><d2p1:VersionDate>0100-01-01T00:00:00</d2p1:VersionDate></d2p1:ProductLocal></d2p1:ProductLocal><d2p1:ProductType>Context</d2p1:ProductType><d2p1:SubOrderTypeCode i:nil="true" /></d2p1:Product><d2p1:ProductCode>Contract</d2p1:ProductCode></d2p1:ProductActionBase><d2p1:ProductActionBase i:type="d2p1:ServiceAction"><d2p1:ActionDate i:nil="true" /><d2p1:ActionType>Add</d2p1:ActionType><d2p1:ChildActions /><d2p1:IsRelation>false</d2p1:IsRelation><d2p1:NeedTariffication>true</d2p1:NeedTariffication><d2p1:OTPrice><d2p1:BasicPrice>30</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>35.40</d2p1:Price><d2p1:ServiceCode>CB9029</d2p1:ServiceCode><d2p1:ServiceId>31</d2p1:ServiceId><d2p1:ServiceName>zzzzzzzzzz zzzzzz zzzzzzzzzzzz zzzzzz</d2p1:ServiceName><d2p1:Tax>5.40</d2p1:Tax></d2p1:OTPrice><d2p1:Parameters><d2p1:ProductActionParameter><d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code><d2p1:Value>1</d2p1:Value></d2p1:ProductActionParameter></d2p1:Parameters><d2p1:ParentPackageId i:nil="true" /><d2p1:Product><d2p1:ChildProducts i:nil="true" /><d2p1:PEPrice><d2p1:BasicPrice>0</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>0</d2p1:Price><d2p1:ServiceCode>CB264</d2p1:ServiceCode><d2p1:ServiceId>30</d2p1:ServiceId><d2p1:ServiceName i:nil="true" /><d2p1:Tax>0</d2p1:Tax></d2p1:PEPrice><d2p1:ProductId><d2p1:ExternalPackageId i:nil="true" /><d2p1:ExternalProductCode>CB264</d2p1:ExternalProductCode><d2p1:ExternalProductId>30</d2p1:ExternalProductId><d2p1:PackageId i:nil="true" /><d2p1:ProductCode>PRODUCT_SERVICE#CB264</d2p1:ProductCode><d2p1:ProductId>10108</d2p1:ProductId><d2p1:VersionDate>2011-11-01T12:14:30</d2p1:VersionDate><d2p1:VersionId>251667</d2p1:VersionId></d2p1:ProductId><d2p1:ProductLocal><d2p1:ProductLocal><d2p1:Description i:nil="true" /><d2p1:Info i:nil="true" /><d2p1:LanguageCode>1</d2p1:LanguageCode><d2p1:Name>zzzzzzzzzzzz zzzzzz</d2p1:Name><d2p1:VersionDate>2011-11-01T12:14:30</d2p1:VersionDate></d2p1:ProductLocal></d2p1:ProductLocal><d2p1:ProductType>Service</d2p1:ProductType><d2p1:SubOrderTypeCode i:nil="true" /></d2p1:Product><d2p1:BonusCampaignId i:nil="true" /><d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier><d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded><d2p1:NeedCheckBlocks i:nil="true" /><d2p1:Quantity i:nil="true" /><d2p1:ServiceId><d2p1:ServiceCode>CB264</d2p1:ServiceCode><d2p1:ServiceId>30</d2p1:ServiceId></d2p1:ServiceId><d2p1:ServiceName>zzzzzzzzzzzz zzzzzz</d2p1:ServiceName><d2p1:TariffPlanId>10</d2p1:TariffPlanId></d2p1:ProductActionBase><d2p1:ProductActionBase i:type="d2p1:ServiceAction"><d2p1:ActionDate i:nil="true" /><d2p1:ActionType>Add</d2p1:ActionType><d2p1:ChildActions /><d2p1:IsRelation>false</d2p1:IsRelation><d2p1:NeedTariffication>true</d2p1:NeedTariffication><d2p1:OTPrice><d2p1:BasicPrice>10</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>11.80</d2p1:Price><d2p1:ServiceCode>ADD3SMS20</d2p1:ServiceCode><d2p1:ServiceId>6551</d2p1:ServiceId><d2p1:ServiceName>zzzzzzzzzz 20 SMS..</d2p1:ServiceName><d2p1:Tax>1.80</d2p1:Tax></d2p1:OTPrice><d2p1:Parameters><d2p1:ProductActionParameter><d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code><d2p1:Value>1</d2p1:Value></d2p1:ProductActionParameter></d2p1:Parameters><d2p1:ParentPackageId i:nil="true" /><d2p1:Product><d2p1:ChildProducts i:nil="true" /><d2p1:PEPrice><d2p1:BasicPrice>10</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>11.80</d2p1:Price><d2p1:ServiceCode>3SMS20</d2p1:ServiceCode><d2p1:ServiceId>6550</d2p1:ServiceId><d2p1:ServiceName i:nil="true" /><d2p1:Tax>1.80</d2p1:Tax></d2p1:PEPrice><d2p1:ProductId><d2p1:ExternalPackageId i:nil="true" /><d2p1:ExternalProductCode>3SMS20</d2p1:ExternalProductCode><d2p1:ExternalProductId>6550</d2p1:ExternalProductId><d2p1:PackageId i:nil="true" /><d2p1:ProductCode>PRODUCT_SERVICE#3SMS20</d2p1:ProductCode><d2p1:ProductId>10206</d2p1:ProductId><d2p1:VersionDate>2011-10-04T10:13:42</d2p1:VersionDate><d2p1:VersionId>147713</d2p1:VersionId></d2p1:ProductId><d2p1:ProductLocal><d2p1:ProductLocal><d2p1:Description i:nil="true" /><d2p1:Info i:nil="true" /><d2p1:LanguageCode>1</d2p1:LanguageCode><d2p1:Name>20 SMS..</d2p1:Name><d2p1:VersionDate>2011-10-04T10:13:42</d2p1:VersionDate></d2p1:ProductLocal></d2p1:ProductLocal><d2p1:ProductType>Service</d2p1:ProductType><d2p1:SubOrderTypeCode i:nil="true" /></d2p1:Product><d2p1:BonusCampaignId i:nil="true" /><d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier><d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded><d2p1:NeedCheckBlocks i:nil="true" /><d2p1:Quantity i:nil="true" /><d2p1:ServiceId><d2p1:ServiceCode>3SMS20</d2p1:ServiceCode><d2p1:ServiceId>6550</d2p1:ServiceId></d2p1:ServiceId><d2p1:ServiceName>20 SMS..</d2p1:ServiceName><d2p1:TariffPlanId>10</d2p1:TariffPlanId></d2p1:ProductActionBase><d2p1:ProductActionBase i:type="d2p1:ServiceAction"><d2p1:ActionDate i:nil="true" /><d2p1:ActionType>Add</d2p1:ActionType><d2p1:ChildActions /><d2p1:IsRelation>false</d2p1:IsRelation><d2p1:NeedTariffication>false</d2p1:NeedTariffication><d2p1:OTPrice><d2p1:BasicPrice>28</d2p1:BasicPrice><d2p1:Discount>28</d2p1:Discount><d2p1:Price>0.00</d2p1:Price><d2p1:ServiceCode>CB9031</d2p1:ServiceCode><d2p1:ServiceId>93</d2p1:ServiceId><d2p1:ServiceName>zzzzzzzzzz zzzzzz zzzzzzzzzzzzzzzz zzzzzz</d2p1:ServiceName><d2p1:Tax>0.00</d2p1:Tax></d2p1:OTPrice><d2p1:Parameters><d2p1:ProductActionParameter><d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code><d2p1:Value>1</d2p1:Value></d2p1:ProductActionParameter></d2p1:Parameters><d2p1:ParentPackageId i:nil="true" /><d2p1:Product><d2p1:ChildProducts i:nil="true" /><d2p1:PEPrice><d2p1:BasicPrice>0</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>0</d2p1:Price><d2p1:ServiceCode>CB534</d2p1:ServiceCode><d2p1:ServiceId>92</d2p1:ServiceId><d2p1:ServiceName i:nil="true" /><d2p1:Tax>0</d2p1:Tax></d2p1:PEPrice><d2p1:ProductId><d2p1:ExternalPackageId i:nil="true" /><d2p1:ExternalProductCode>CB534</d2p1:ExternalProductCode><d2p1:ExternalProductId>92</d2p1:ExternalProductId><d2p1:PackageId i:nil="true" /><d2p1:ProductCode>PRODUCT_SERVICE#CB534</d2p1:ProductCode><d2p1:ProductId>24</d2p1:ProductId><d2p1:VersionDate>2011-06-06T11:51:52</d2p1:VersionDate><d2p1:VersionId>40128</d2p1:VersionId></d2p1:ProductId><d2p1:ProductLocal><d2p1:ProductLocal><d2p1:Description>zzzzz!
zzzz!
zzzzzz!
zzzzzzzzzzzzzzzz!</d2p1:Description><d2p1:Info i:nil="true" /><d2p1:LanguageCode>1</d2p1:LanguageCode><d2p1:Name>zzzzzzzzzzzzzzzz zzzzzz</d2p1:Name><d2p1:VersionDate>2011-06-06T11:51:52</d2p1:VersionDate></d2p1:ProductLocal></d2p1:ProductLocal><d2p1:ProductType>Service</d2p1:ProductType><d2p1:SubOrderTypeCode i:nil="true" /></d2p1:Product><d2p1:BonusCampaignId i:nil="true" /><d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier><d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded><d2p1:NeedCheckBlocks i:nil="true" /><d2p1:Quantity i:nil="true" /><d2p1:ServiceId><d2p1:ServiceCode>CB534</d2p1:ServiceCode><d2p1:ServiceId>92</d2p1:ServiceId></d2p1:ServiceId><d2p1:ServiceName>zzzzzzzzzzzzzzzz zzzzzz</d2p1:ServiceName><d2p1:TariffPlanId>10</d2p1:TariffPlanId></d2p1:ProductActionBase><d2p1:ProductActionBase i:type="d2p1:ServiceAction"><d2p1:ActionDate i:nil="true" /><d2p1:ActionType>Delete</d2p1:ActionType><d2p1:ChildActions /><d2p1:IsRelation>false</d2p1:IsRelation><d2p1:NeedTariffication>false</d2p1:NeedTariffication><d2p1:OTPrice><d2p1:BasicPrice>0</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>0.00</d2p1:Price><d2p1:ServiceCode>CB9024</d2p1:ServiceCode><d2p1:ServiceId>43</d2p1:ServiceId><d2p1:ServiceName>zzzzzzzz zzzzzz zzzzzzzzzzzzz zzzzzz</d2p1:ServiceName><d2p1:Tax>0.00</d2p1:Tax></d2p1:OTPrice><d2p1:Parameters><d2p1:ProductActionParameter><d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code><d2p1:Value>1</d2p1:Value></d2p1:ProductActionParameter></d2p1:Parameters><d2p1:ParentPackageId i:nil="true" /><d2p1:Product><d2p1:ChildProducts i:nil="true" /><d2p1:PEPrice><d2p1:BasicPrice>0</d2p1:BasicPrice><d2p1:Discount>0</d2p1:Discount><d2p1:Price>0.00</d2p1:Price><d2p1:ServiceCode>CB108</d2p1:ServiceCode><d2p1:ServiceId>40</d2p1:ServiceId><d2p1:ServiceName i:nil="true" /><d2p1:Tax>0.00</d2p1:Tax></d2p1:PEPrice><d2p1:ProductId><d2p1:ExternalPackageId i:nil="true" /><d2p1:ExternalProductCode>CB108</d2p1:ExternalProductCode><d2p1:ExternalProductId>40</d2p1:ExternalProductId><d2p1:PackageId i:nil="true" /><d2p1:ProductCode>PRODUCT_SERVICE#CB108</d2p1:ProductCode><d2p1:ProductId>10066</d2p1:ProductId><d2p1:VersionDate>2011-10-10T14:42:32</d2p1:VersionDate><d2p1:VersionId>167201</d2p1:VersionId></d2p1:ProductId><d2p1:ProductLocal><d2p1:ProductLocal><d2p1:Description i:nil="true" /><d2p1:Info i:nil="true" /><d2p1:LanguageCode>1</d2p1:LanguageCode><d2p1:Name>zzzzzzzzzzzzz zzzzzz</d2p1:Name><d2p1:VersionDate>2011-10-10T14:42:32</d2p1:VersionDate></d2p1:ProductLocal></d2p1:ProductLocal><d2p1:ProductType>Service</d2p1:ProductType><d2p1:SubOrderTypeCode i:nil="true" /></d2p1:Product><d2p1:BonusCampaignId i:nil="true" /><d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier><d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded><d2p1:NeedCheckBlocks i:nil="true" /><d2p1:Quantity i:nil="true" /><d2p1:ServiceId><d2p1:ServiceCode>CB108</d2p1:ServiceCode><d2p1:ServiceId>40</d2p1:ServiceId></d2p1:ServiceId><d2p1:ServiceName>zzzzzzzzzzzzz zzzzzz</d2p1:ServiceName><d2p1:TariffPlanId>11</d2p1:TariffPlanId></d2p1:ProductActionBase></Actions><ResultServices><ConnectedService><DateFrom>2011-10-12T11:49:45</DateFrom><ServiceCode>per11</ServiceCode><ServiceId>6727</ServiceId></ConnectedService><ConnectedService><DateFrom>2011-10-12T11:49:45</DateFrom><ServiceCode>100ABOND</ServiceCode><ServiceId>6947</ServiceId></ConnectedService><ConnectedService><DateFrom>2011-10-12T11:49:45</DateFrom><ServiceCode>ZgpRed</ServiceCode><ServiceId>6307</ServiceId></ConnectedService><ConnectedService><DateFrom>2011-10-12T11:49:45</DateFrom><ServiceCode>CB59</ServiceCode><ServiceId>24</ServiceId></ConnectedService><ConnectedService><DateFrom>2011-10-12T11:49:45</DateFrom><ServiceCode>CB10555</ServiceCode><ServiceId>61</ServiceId></ConnectedService><ConnectedService><DateFrom>2011-12-06T14:55:28</DateFrom><ServiceCode>TESTU9</ServiceCode><ServiceId>11428</ServiceId></ConnectedService><ConnectedService><DateFrom>2011-12-06T14:55:28</DateFrom><ServiceCode>TESTU2</ServiceCode><ServiceId>11421</ServiceId></ConnectedService><ConnectedService><DateFrom>2011-12-06T14:55:28</DateFrom><ServiceCode>CB111715</ServiceCode><ServiceId>5810</ServiceId></ConnectedService><ConnectedService><DateFrom i:nil="true" /><ServiceCode>CB264</ServiceCode><ServiceId>30</ServiceId></ConnectedService><ConnectedService><DateFrom i:nil="true" /><ServiceCode>3SMS20</ServiceCode><ServiceId>6550</ServiceId></ConnectedService><ConnectedService><DateFrom i:nil="true" /><ServiceCode>CB534</ServiceCode><ServiceId>92</ServiceId></ConnectedService></ResultServices></ProductsContainer>""",
"""[13:07:04.8158468][thread 9] \t\tSaving attribute: attId=1683, dataTypeId=tpLongText, table_row_id=, value=<?xml version="1.0" encoding="utf-16"?>
<ProductsContainer xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Messages/v001">
    <Actions xmlns:d2p1="http://schemas.sitels.ru/OrderManagement.BusinessProcess.Contracts/v001">
        <d2p1:ProductActionBase i:type="d2p1:TariffPlanAction">
            <d2p1:ActionDate i:nil="true" />
            <d2p1:ActionType>Delete</d2p1:ActionType>
            <d2p1:ChildActions />
            <d2p1:IsRelation>false</d2p1:IsRelation>
            <d2p1:NeedTariffication>true</d2p1:NeedTariffication>
            <d2p1:OTPrice i:nil="true" />
            <d2p1:Parameters />
            <d2p1:ParentPackageId i:nil="true" />
            <d2p1:Product>
                <d2p1:ChildProducts i:nil="true" />
                <d2p1:PEPrice i:nil="true" />
                <d2p1:ProductId>
                    <d2p1:ExternalPackageId i:nil="true" />
                    <d2p1:ExternalProductCode>11</d2p1:ExternalProductCode>
                    <d2p1:ExternalProductId>11</d2p1:ExternalProductId>
                    <d2p1:PackageId i:nil="true" />
                    <d2p1:ProductCode>TariffPlan#11</d2p1:ProductCode>
                    <d2p1:ProductId>9952</d2p1:ProductId>
                    <d2p1:VersionDate>2011-10-27T11:42:10</d2p1:VersionDate>
                    <d2p1:VersionId>242123</d2p1:VersionId>
                </d2p1:ProductId>
                <d2p1:ProductLocal>
                    <d2p1:ProductLocal>
                        <d2p1:Description i:nil="true" />
                        <d2p1:Info i:nil="true" />
                        <d2p1:LanguageCode>1</d2p1:LanguageCode>
                        <d2p1:Name>zzz zzzzzz - zzzzzz 200</d2p1:Name>
                        <d2p1:VersionDate>2011-10-27T11:42:10</d2p1:VersionDate>
                    </d2p1:ProductLocal>
                </d2p1:ProductLocal>
                <d2p1:ProductType>TariffPlan</d2p1:ProductType>
                <d2p1:SubOrderTypeCode i:nil="true" />
            </d2p1:Product>
            <d2p1:TariffPlanCode i:nil="true" />
            <d2p1:TariffPlanId>11</d2p1:TariffPlanId>
        </d2p1:ProductActionBase>
        <d2p1:ProductActionBase i:type="d2p1:TariffPlanAction">
            <d2p1:ActionDate i:nil="true" />
            <d2p1:ActionType>Add</d2p1:ActionType>
            <d2p1:ChildActions />
            <d2p1:IsRelation>false</d2p1:IsRelation>
            <d2p1:NeedTariffication>true</d2p1:NeedTariffication>
            <d2p1:OTPrice>
                <d2p1:BasicPrice>50</d2p1:BasicPrice>
                <d2p1:Discount>0</d2p1:Discount>
                <d2p1:Price>59.00</d2p1:Price>
                <d2p1:ServiceCode>FRCHB</d2p1:ServiceCode>
                <d2p1:ServiceId>4260</d2p1:ServiceId>
                <d2p1:ServiceName>zzzzz zzzzzzzzz zzzzz zz zzzzz zzzzzzz zz</d2p1:ServiceName>
                <d2p1:Tax>9.00</d2p1:Tax>
            </d2p1:OTPrice>
            <d2p1:Parameters>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>NewCalculationMethodAlgorithm</d2p1:Code>
                    <d2p1:Value>Profile</d2p1:Value>
                </d2p1:ProductActionParameter>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>NewTrustCategoryAlgorithm</d2p1:Code>
                    <d2p1:Value>Recommended</d2p1:Value>
                </d2p1:ProductActionParameter>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>NewMarketingCategoryAlgorithm</d2p1:Code>
                    <d2p1:Value>NotChange</d2p1:Value>
                </d2p1:ProductActionParameter>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code>
                    <d2p1:Value>0</d2p1:Value>
                </d2p1:ProductActionParameter>
            </d2p1:Parameters>
            <d2p1:ParentPackageId i:nil="true" />
            <d2p1:Product>
                <d2p1:ChildProducts i:nil="true" />
                <d2p1:PEPrice i:nil="true" />
                <d2p1:ProductId>
                    <d2p1:ExternalPackageId i:nil="true" />
                    <d2p1:ExternalProductCode>10</d2p1:ExternalProductCode>
                    <d2p1:ExternalProductId>10</d2p1:ExternalProductId>
                    <d2p1:PackageId i:nil="true" />
                    <d2p1:ProductCode>TariffPlan#10</d2p1:ProductCode>
                    <d2p1:ProductId>9951</d2p1:ProductId>
                    <d2p1:VersionDate>2011-10-03T14:26:04</d2p1:VersionDate>
                    <d2p1:VersionId>141944</d2p1:VersionId>
                </d2p1:ProductId>
                <d2p1:ProductLocal>
                    <d2p1:ProductLocal>
                        <d2p1:Description i:nil="true" />
                        <d2p1:Info i:nil="true" />
                        <d2p1:LanguageCode>1</d2p1:LanguageCode>
                        <d2p1:Name>zzz zzzzzz - zzzzzz 100</d2p1:Name>
                        <d2p1:VersionDate>2011-10-03T14:26:04</d2p1:VersionDate>
                    </d2p1:ProductLocal>
                </d2p1:ProductLocal>
                <d2p1:ProductType>TariffPlan</d2p1:ProductType>
                <d2p1:SubOrderTypeCode i:nil="true" />
            </d2p1:Product>
            <d2p1:TariffPlanCode>10</d2p1:TariffPlanCode>
            <d2p1:TariffPlanId>10</d2p1:TariffPlanId>
        </d2p1:ProductActionBase>
        <d2p1:ProductActionBase i:type="d2p1:ContextProductAction">
            <d2p1:ActionDate i:nil="true" />
            <d2p1:ActionType>Modify</d2p1:ActionType>
            <d2p1:ChildActions />
            <d2p1:IsRelation>false</d2p1:IsRelation>
            <d2p1:NeedTariffication>true</d2p1:NeedTariffication>
            <d2p1:OTPrice i:nil="true" />
            <d2p1:Parameters />
            <d2p1:ParentPackageId i:nil="true" />
            <d2p1:Product>
                <d2p1:ChildProducts i:nil="true" />
                <d2p1:PEPrice i:nil="true" />
                <d2p1:ProductId>
                    <d2p1:ExternalPackageId i:nil="true" />
                    <d2p1:ExternalProductCode i:nil="true" />
                    <d2p1:ExternalProductId i:nil="true" />
                    <d2p1:PackageId i:nil="true" />
                    <d2p1:ProductCode>Contract</d2p1:ProductCode>
                    <d2p1:ProductId>10698</d2p1:ProductId>
                    <d2p1:VersionDate>0100-01-01T00:00:00</d2p1:VersionDate>
                    <d2p1:VersionId>11219</d2p1:VersionId>
                </d2p1:ProductId>
                <d2p1:ProductLocal>
                    <d2p1:ProductLocal>
                        <d2p1:Description i:nil="true" />
                        <d2p1:Info i:nil="true" />
                        <d2p1:LanguageCode>1</d2p1:LanguageCode>
                        <d2p1:Name>zzzzzzzz</d2p1:Name>
                        <d2p1:VersionDate>0100-01-01T00:00:00</d2p1:VersionDate>
                    </d2p1:ProductLocal>
                </d2p1:ProductLocal>
                <d2p1:ProductType>Context</d2p1:ProductType>
                <d2p1:SubOrderTypeCode i:nil="true" />
            </d2p1:Product>
            <d2p1:ProductCode>Contract</d2p1:ProductCode>
        </d2p1:ProductActionBase>
        <d2p1:ProductActionBase i:type="d2p1:ServiceAction">
            <d2p1:ActionDate i:nil="true" />
            <d2p1:ActionType>Add</d2p1:ActionType>
            <d2p1:ChildActions />
            <d2p1:IsRelation>false</d2p1:IsRelation>
            <d2p1:NeedTariffication>true</d2p1:NeedTariffication>
            <d2p1:OTPrice>
                <d2p1:BasicPrice>30</d2p1:BasicPrice>
                <d2p1:Discount>0</d2p1:Discount>
                <d2p1:Price>35.40</d2p1:Price>
                <d2p1:ServiceCode>CB9029</d2p1:ServiceCode>
                <d2p1:ServiceId>31</d2p1:ServiceId>
                <d2p1:ServiceName>zzzzzzzzzz zzzzzz zzzzzzzzzzzz zzzzzz</d2p1:ServiceName>
                <d2p1:Tax>5.40</d2p1:Tax>
            </d2p1:OTPrice>
            <d2p1:Parameters>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code>
                    <d2p1:Value>1</d2p1:Value>
                </d2p1:ProductActionParameter>
            </d2p1:Parameters>
            <d2p1:ParentPackageId i:nil="true" />
            <d2p1:Product>
                <d2p1:ChildProducts i:nil="true" />
                <d2p1:PEPrice>
                    <d2p1:BasicPrice>0</d2p1:BasicPrice>
                    <d2p1:Discount>0</d2p1:Discount>
                    <d2p1:Price>0</d2p1:Price>
                    <d2p1:ServiceCode>CB264</d2p1:ServiceCode>
                    <d2p1:ServiceId>30</d2p1:ServiceId>
                    <d2p1:ServiceName i:nil="true" />
                    <d2p1:Tax>0</d2p1:Tax>
                </d2p1:PEPrice>
                <d2p1:ProductId>
                    <d2p1:ExternalPackageId i:nil="true" />
                    <d2p1:ExternalProductCode>CB264</d2p1:ExternalProductCode>
                    <d2p1:ExternalProductId>30</d2p1:ExternalProductId>
                    <d2p1:PackageId i:nil="true" />
                    <d2p1:ProductCode>PRODUCT_SERVICE#CB264</d2p1:ProductCode>
                    <d2p1:ProductId>10108</d2p1:ProductId>
                    <d2p1:VersionDate>2011-11-01T12:14:30</d2p1:VersionDate>
                    <d2p1:VersionId>251667</d2p1:VersionId>
                </d2p1:ProductId>
                <d2p1:ProductLocal>
                    <d2p1:ProductLocal>
                        <d2p1:Description i:nil="true" />
                        <d2p1:Info i:nil="true" />
                        <d2p1:LanguageCode>1</d2p1:LanguageCode>
                        <d2p1:Name>zzzzzzzzzzzz zzzzzz</d2p1:Name>
                        <d2p1:VersionDate>2011-11-01T12:14:30</d2p1:VersionDate>
                    </d2p1:ProductLocal>
                </d2p1:ProductLocal>
                <d2p1:ProductType>Service</d2p1:ProductType>
                <d2p1:SubOrderTypeCode i:nil="true" />
            </d2p1:Product>
            <d2p1:BonusCampaignId i:nil="true" />
            <d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
            <d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded>
            <d2p1:NeedCheckBlocks i:nil="true" />
            <d2p1:Quantity i:nil="true" />
            <d2p1:ServiceId>
                <d2p1:ServiceCode>CB264</d2p1:ServiceCode>
                <d2p1:ServiceId>30</d2p1:ServiceId>
            </d2p1:ServiceId>
            <d2p1:ServiceName>zzzzzzzzzzzz zzzzzz</d2p1:ServiceName>
            <d2p1:TariffPlanId>10</d2p1:TariffPlanId>
        </d2p1:ProductActionBase>
        <d2p1:ProductActionBase i:type="d2p1:ServiceAction">
            <d2p1:ActionDate i:nil="true" />
            <d2p1:ActionType>Add</d2p1:ActionType>
            <d2p1:ChildActions />
            <d2p1:IsRelation>false</d2p1:IsRelation>
            <d2p1:NeedTariffication>true</d2p1:NeedTariffication>
            <d2p1:OTPrice>
                <d2p1:BasicPrice>10</d2p1:BasicPrice>
                <d2p1:Discount>0</d2p1:Discount>
                <d2p1:Price>11.80</d2p1:Price>
                <d2p1:ServiceCode>ADD3SMS20</d2p1:ServiceCode>
                <d2p1:ServiceId>6551</d2p1:ServiceId>
                <d2p1:ServiceName>zzzzzzzzzz 20 SMS..</d2p1:ServiceName>
                <d2p1:Tax>1.80</d2p1:Tax>
            </d2p1:OTPrice>
            <d2p1:Parameters>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code>
                    <d2p1:Value>1</d2p1:Value>
                </d2p1:ProductActionParameter>
            </d2p1:Parameters>
            <d2p1:ParentPackageId i:nil="true" />
            <d2p1:Product>
                <d2p1:ChildProducts i:nil="true" />
                <d2p1:PEPrice>
                    <d2p1:BasicPrice>10</d2p1:BasicPrice>
                    <d2p1:Discount>0</d2p1:Discount>
                    <d2p1:Price>11.80</d2p1:Price>
                    <d2p1:ServiceCode>3SMS20</d2p1:ServiceCode>
                    <d2p1:ServiceId>6550</d2p1:ServiceId>
                    <d2p1:ServiceName i:nil="true" />
                    <d2p1:Tax>1.80</d2p1:Tax>
                </d2p1:PEPrice>
                <d2p1:ProductId>
                    <d2p1:ExternalPackageId i:nil="true" />
                    <d2p1:ExternalProductCode>3SMS20</d2p1:ExternalProductCode>
                    <d2p1:ExternalProductId>6550</d2p1:ExternalProductId>
                    <d2p1:PackageId i:nil="true" />
                    <d2p1:ProductCode>PRODUCT_SERVICE#3SMS20</d2p1:ProductCode>
                    <d2p1:ProductId>10206</d2p1:ProductId>
                    <d2p1:VersionDate>2011-10-04T10:13:42</d2p1:VersionDate>
                    <d2p1:VersionId>147713</d2p1:VersionId>
                </d2p1:ProductId>
                <d2p1:ProductLocal>
                    <d2p1:ProductLocal>
                        <d2p1:Description i:nil="true" />
                        <d2p1:Info i:nil="true" />
                        <d2p1:LanguageCode>1</d2p1:LanguageCode>
                        <d2p1:Name>20 SMS..</d2p1:Name>
                        <d2p1:VersionDate>2011-10-04T10:13:42</d2p1:VersionDate>
                    </d2p1:ProductLocal>
                </d2p1:ProductLocal>
                <d2p1:ProductType>Service</d2p1:ProductType>
                <d2p1:SubOrderTypeCode i:nil="true" />
            </d2p1:Product>
            <d2p1:BonusCampaignId i:nil="true" />
            <d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
            <d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded>
            <d2p1:NeedCheckBlocks i:nil="true" />
            <d2p1:Quantity i:nil="true" />
            <d2p1:ServiceId>
                <d2p1:ServiceCode>3SMS20</d2p1:ServiceCode>
                <d2p1:ServiceId>6550</d2p1:ServiceId>
            </d2p1:ServiceId>
            <d2p1:ServiceName>20 SMS..</d2p1:ServiceName>
            <d2p1:TariffPlanId>10</d2p1:TariffPlanId>
        </d2p1:ProductActionBase>
        <d2p1:ProductActionBase i:type="d2p1:ServiceAction">
            <d2p1:ActionDate i:nil="true" />
            <d2p1:ActionType>Add</d2p1:ActionType>
            <d2p1:ChildActions />
            <d2p1:IsRelation>false</d2p1:IsRelation>
            <d2p1:NeedTariffication>false</d2p1:NeedTariffication>
            <d2p1:OTPrice>
                <d2p1:BasicPrice>28</d2p1:BasicPrice>
                <d2p1:Discount>28</d2p1:Discount>
                <d2p1:Price>0.00</d2p1:Price>
                <d2p1:ServiceCode>CB9031</d2p1:ServiceCode>
                <d2p1:ServiceId>93</d2p1:ServiceId>
                <d2p1:ServiceName>zzzzzzzzzz zzzzzz zzzzzzzzzzzzzzzz zzzzzz</d2p1:ServiceName>
                <d2p1:Tax>0.00</d2p1:Tax>
            </d2p1:OTPrice>
            <d2p1:Parameters>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code>
                    <d2p1:Value>1</d2p1:Value>
                </d2p1:ProductActionParameter>
            </d2p1:Parameters>
            <d2p1:ParentPackageId i:nil="true" />
            <d2p1:Product>
                <d2p1:ChildProducts i:nil="true" />
                <d2p1:PEPrice>
                    <d2p1:BasicPrice>0</d2p1:BasicPrice>
                    <d2p1:Discount>0</d2p1:Discount>
                    <d2p1:Price>0</d2p1:Price>
                    <d2p1:ServiceCode>CB534</d2p1:ServiceCode>
                    <d2p1:ServiceId>92</d2p1:ServiceId>
                    <d2p1:ServiceName i:nil="true" />
                    <d2p1:Tax>0</d2p1:Tax>
                </d2p1:PEPrice>
                <d2p1:ProductId>
                    <d2p1:ExternalPackageId i:nil="true" />
                    <d2p1:ExternalProductCode>CB534</d2p1:ExternalProductCode>
                    <d2p1:ExternalProductId>92</d2p1:ExternalProductId>
                    <d2p1:PackageId i:nil="true" />
                    <d2p1:ProductCode>PRODUCT_SERVICE#CB534</d2p1:ProductCode>
                    <d2p1:ProductId>24</d2p1:ProductId>
                    <d2p1:VersionDate>2011-06-06T11:51:52</d2p1:VersionDate>
                    <d2p1:VersionId>40128</d2p1:VersionId>
                </d2p1:ProductId>
                <d2p1:ProductLocal>
                    <d2p1:ProductLocal>
                        <d2p1:Description>zzzzz!
zzzz!
zzzzzz!
zzzzzzzzzzzzzzzz!</d2p1:Description>
                        <d2p1:Info i:nil="true" />
                        <d2p1:LanguageCode>1</d2p1:LanguageCode>
                        <d2p1:Name>zzzzzzzzzzzzzzzz zzzzzz</d2p1:Name>
                        <d2p1:VersionDate>2011-06-06T11:51:52</d2p1:VersionDate>
                    </d2p1:ProductLocal>
                </d2p1:ProductLocal>
                <d2p1:ProductType>Service</d2p1:ProductType>
                <d2p1:SubOrderTypeCode i:nil="true" />
            </d2p1:Product>
            <d2p1:BonusCampaignId i:nil="true" />
            <d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
            <d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded>
            <d2p1:NeedCheckBlocks i:nil="true" />
            <d2p1:Quantity i:nil="true" />
            <d2p1:ServiceId>
                <d2p1:ServiceCode>CB534</d2p1:ServiceCode>
                <d2p1:ServiceId>92</d2p1:ServiceId>
            </d2p1:ServiceId>
            <d2p1:ServiceName>zzzzzzzzzzzzzzzz zzzzzz</d2p1:ServiceName>
            <d2p1:TariffPlanId>10</d2p1:TariffPlanId>
        </d2p1:ProductActionBase>
        <d2p1:ProductActionBase i:type="d2p1:ServiceAction">
            <d2p1:ActionDate i:nil="true" />
            <d2p1:ActionType>Delete</d2p1:ActionType>
            <d2p1:ChildActions />
            <d2p1:IsRelation>false</d2p1:IsRelation>
            <d2p1:NeedTariffication>false</d2p1:NeedTariffication>
            <d2p1:OTPrice>
                <d2p1:BasicPrice>0</d2p1:BasicPrice>
                <d2p1:Discount>0</d2p1:Discount>
                <d2p1:Price>0.00</d2p1:Price>
                <d2p1:ServiceCode>CB9024</d2p1:ServiceCode>
                <d2p1:ServiceId>43</d2p1:ServiceId>
                <d2p1:ServiceName>zzzzzzzz zzzzzz zzzzzzzzzzzzz zzzzzz</d2p1:ServiceName>
                <d2p1:Tax>0.00</d2p1:Tax>
            </d2p1:OTPrice>
            <d2p1:Parameters>
                <d2p1:ProductActionParameter>
                    <d2p1:Code>IsUseSpaForFinancialPlatform</d2p1:Code>
                    <d2p1:Value>1</d2p1:Value>
                </d2p1:ProductActionParameter>
            </d2p1:Parameters>
            <d2p1:ParentPackageId i:nil="true" />
            <d2p1:Product>
                <d2p1:ChildProducts i:nil="true" />
                <d2p1:PEPrice>
                    <d2p1:BasicPrice>0</d2p1:BasicPrice>
                    <d2p1:Discount>0</d2p1:Discount>
                    <d2p1:Price>0.00</d2p1:Price>
                    <d2p1:ServiceCode>CB108</d2p1:ServiceCode>
                    <d2p1:ServiceId>40</d2p1:ServiceId>
                    <d2p1:ServiceName i:nil="true" />
                    <d2p1:Tax>0.00</d2p1:Tax>
                </d2p1:PEPrice>
                <d2p1:ProductId>
                    <d2p1:ExternalPackageId i:nil="true" />
                    <d2p1:ExternalProductCode>CB108</d2p1:ExternalProductCode>
                    <d2p1:ExternalProductId>40</d2p1:ExternalProductId>
                    <d2p1:PackageId i:nil="true" />
                    <d2p1:ProductCode>PRODUCT_SERVICE#CB108</d2p1:ProductCode>
                    <d2p1:ProductId>10066</d2p1:ProductId>
                    <d2p1:VersionDate>2011-10-10T14:42:32</d2p1:VersionDate>
                    <d2p1:VersionId>167201</d2p1:VersionId>
                </d2p1:ProductId>
                <d2p1:ProductLocal>
                    <d2p1:ProductLocal>
                        <d2p1:Description i:nil="true" />
                        <d2p1:Info i:nil="true" />
                        <d2p1:LanguageCode>1</d2p1:LanguageCode>
                        <d2p1:Name>zzzzzzzzzzzzz zzzzzz</d2p1:Name>
                        <d2p1:VersionDate>2011-10-10T14:42:32</d2p1:VersionDate>
                    </d2p1:ProductLocal>
                </d2p1:ProductLocal>
                <d2p1:ProductType>Service</d2p1:ProductType>
                <d2p1:SubOrderTypeCode i:nil="true" />
            </d2p1:Product>
            <d2p1:BonusCampaignId i:nil="true" />
            <d2p1:ExternalSystemIdentifier>0</d2p1:ExternalSystemIdentifier>
            <d2p1:IsAutomaticAdded>true</d2p1:IsAutomaticAdded>
            <d2p1:NeedCheckBlocks i:nil="true" />
            <d2p1:Quantity i:nil="true" />
            <d2p1:ServiceId>
                <d2p1:ServiceCode>CB108</d2p1:ServiceCode>
                <d2p1:ServiceId>40</d2p1:ServiceId>
            </d2p1:ServiceId>
            <d2p1:ServiceName>zzzzzzzzzzzzz zzzzzz</d2p1:ServiceName>
            <d2p1:TariffPlanId>11</d2p1:TariffPlanId>
        </d2p1:ProductActionBase>
    </Actions>
    <ResultServices>
        <ConnectedService>
            <DateFrom>2011-10-12T11:49:45</DateFrom>
            <ServiceCode>per11</ServiceCode>
            <ServiceId>6727</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom>2011-10-12T11:49:45</DateFrom>
            <ServiceCode>100ABOND</ServiceCode>
            <ServiceId>6947</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom>2011-10-12T11:49:45</DateFrom>
            <ServiceCode>ZgpRed</ServiceCode>
            <ServiceId>6307</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom>2011-10-12T11:49:45</DateFrom>
            <ServiceCode>CB59</ServiceCode>
            <ServiceId>24</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom>2011-10-12T11:49:45</DateFrom>
            <ServiceCode>CB10555</ServiceCode>
            <ServiceId>61</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom>2011-12-06T14:55:28</DateFrom>
            <ServiceCode>TESTU9</ServiceCode>
            <ServiceId>11428</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom>2011-12-06T14:55:28</DateFrom>
            <ServiceCode>TESTU2</ServiceCode>
            <ServiceId>11421</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom>2011-12-06T14:55:28</DateFrom>
            <ServiceCode>CB111715</ServiceCode>
            <ServiceId>5810</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom i:nil="true" />
            <ServiceCode>CB264</ServiceCode>
            <ServiceId>30</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom i:nil="true" />
            <ServiceCode>3SMS20</ServiceCode>
            <ServiceId>6550</ServiceId>
        </ConnectedService>
        <ConnectedService>
            <DateFrom i:nil="true" />
            <ServiceCode>CB534</ServiceCode>
            <ServiceId>92</ServiceId>
        </ConnectedService>
    </ResultServices>
</ProductsContainer>"""),
("""2011-12-07 14:59:06,347 [1] DEBUG
=======================================
0 - GetPAsWithTDWithPrepaidTariffPlansByPaIds - process parameter oneTdOnPaTariffPlans=<Table><Row><TARIFF_PLAN_ID>486</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>486</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz 0.07 (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>3;13;23</EXTERNAL_CODE><EXTERNAL_CODE2>13</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>7001</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>7001</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzzzzzzzz</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>2</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>12;</EXTERNAL_CODE><EXTERNAL_CODE2>12;</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>6</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>7012</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>7012</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz - 300 zzz.</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>7012</EXTERNAL_CODE><EXTERNAL_CODE2>7012</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>8010</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>7999</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzz + zzzzzz zzz</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>7000</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>AD</TARIFF_PLAN_TYPE><EXTERNAL_CODE>248</EXTERNAL_CODE><EXTERNAL_CODE2>248</EXTERNAL_CODE2><EXTERNAL_CODE3>248</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>8673</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>8673</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz 200 [SCP]</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>3</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>8673</EXTERNAL_CODE><EXTERNAL_CODE2>8673</EXTERNAL_CODE2><EXTERNAL_CODE3>null</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>6</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>388</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>388</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz zzzzzzz (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>8;18;28</EXTERNAL_CODE><EXTERNAL_CODE2>18</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>6694</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>6694</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzzzzz (zzzz zzzz-zzz)  - zzzzz 0.07 + zzzzzzz (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>93;</EXTERNAL_CODE><EXTERNAL_CODE2>93</EXTERNAL_CODE2><EXTERNAL_CODE3>434</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>7832</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>TMP000122</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>Copy of zzz zzzzzz - zzzzz 0.07 (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>TMP000234</EXTERNAL_CODE><EXTERNAL_CODE2>TMP000345</EXTERNAL_CODE2><EXTERNAL_CODE3>null</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>485</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>485</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz zzzzz (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>5;15;25</EXTERNAL_CODE><EXTERNAL_CODE2>15</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>7004</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>7004</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzz</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>3</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>7004</EXTERNAL_CODE><EXTERNAL_CODE2>7004</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>6604</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>6604</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz 400 (zzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>6604;</EXTERNAL_CODE><EXTERNAL_CODE2>6604</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>8631</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>8631</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzzzzzzzzz zz. zzzzzzzzzz zzzzzzz</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>7000</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>zzz zzzzzzzzzzzz zzzzz zzzzzzzzzzz</DESCRIPTION><TARIFF_PLAN_TYPE>AD</TARIFF_PLAN_TYPE><EXTERNAL_CODE>8631</EXTERNAL_CODE><EXTERNAL_CODE2>8631</EXTERNAL_CODE2><EXTERNAL_CODE3>8631</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>605</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>8671</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>OPT10_SCP</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz 100 [SCP]</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>2</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>OPT10_SCP</EXTERNAL_CODE><EXTERNAL_CODE2>OPT10_SCP</EXTERNAL_CODE2><EXTERNAL_CODE3>null</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>6693</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>6693</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzzzzz (zzzz zzzz-zzz)  - zzzzz 0.07 + zzzzzzz (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>94;</EXTERNAL_CODE><EXTERNAL_CODE2>94</EXTERNAL_CODE2><EXTERNAL_CODE3>434</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>386</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>386</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz 0.07 (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>14</EXTERNAL_CODE><EXTERNAL_CODE2>14</EXTERNAL_CODE2><EXTERNAL_CODE3>525386</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>488</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>488</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>MTC Moczza - zzzzc zzacczz (zocezzzzzo c 1 cezzzzz)111</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>17</EXTERNAL_CODE><EXTERNAL_CODE2>17</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>7000</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>7000</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzz</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>7000</EXTERNAL_CODE><EXTERNAL_CODE2>7000</EXTERNAL_CODE2><EXTERNAL_CODE3>7000</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>2</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>7002</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>7002</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzz zzzz</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>13;</EXTERNAL_CODE><EXTERNAL_CODE2>13;</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row><Row><TARIFF_PLAN_ID>9900</TARIFF_PLAN_ID><TARIFF_PLAN_CODE>9900</TARIFF_PLAN_CODE><TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz zzz zzzzz zzzzzzz (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME><TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2><BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID><MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES><DESCRIPTION>null</DESCRIPTION><TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE><EXTERNAL_CODE>9900</EXTERNAL_CODE><EXTERNAL_CODE2>9900</EXTERNAL_CODE2><EXTERNAL_CODE3>525</EXTERNAL_CODE3><SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID><MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION></Row></Table>
=======================================""",
"""2011-12-07 14:59:06,347 [1] DEBUG
=======================================
0 - GetPAsWithTDWithPrepaidTariffPlansByPaIds - process parameter oneTdOnPaTariffPlans=<Table>
    <Row>
        <TARIFF_PLAN_ID>486</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>486</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz 0.07 (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>3;13;23</EXTERNAL_CODE>
        <EXTERNAL_CODE2>13</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>7001</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>7001</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzzzzzzzz</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>2</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>12;</EXTERNAL_CODE>
        <EXTERNAL_CODE2>12;</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>6</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>7012</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>7012</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz - 300 zzz.</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>7012</EXTERNAL_CODE>
        <EXTERNAL_CODE2>7012</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>8010</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>7999</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzz + zzzzzz zzz</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>7000</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>AD</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>248</EXTERNAL_CODE>
        <EXTERNAL_CODE2>248</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>248</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>8673</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>8673</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz 200 [SCP]</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>3</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>8673</EXTERNAL_CODE>
        <EXTERNAL_CODE2>8673</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>null</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>6</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>388</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>388</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz zzzzzzz (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>8;18;28</EXTERNAL_CODE>
        <EXTERNAL_CODE2>18</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>6694</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>6694</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzzzzz (zzzz zzzz-zzz)  - zzzzz 0.07 + zzzzzzz (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>93;</EXTERNAL_CODE>
        <EXTERNAL_CODE2>93</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>434</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>7832</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>TMP000122</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>Copy of zzz zzzzzz - zzzzz 0.07 (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>TMP000234</EXTERNAL_CODE>
        <EXTERNAL_CODE2>TMP000345</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>null</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>485</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>485</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz zzzzz (zzzzzzzzzz z 1 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>5;15;25</EXTERNAL_CODE>
        <EXTERNAL_CODE2>15</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>7004</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>7004</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzz</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>3</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>7004</EXTERNAL_CODE>
        <EXTERNAL_CODE2>7004</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>6604</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>6604</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz 400 (zzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>6604;</EXTERNAL_CODE>
        <EXTERNAL_CODE2>6604</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>8631</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>8631</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzzzzzzzzz zz. zzzzzzzzzz zzzzzzz</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>7000</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>zzz zzzzzzzzzzzz zzzzz zzzzzzzzzzz</DESCRIPTION>
        <TARIFF_PLAN_TYPE>AD</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>8631</EXTERNAL_CODE>
        <EXTERNAL_CODE2>8631</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>8631</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>605</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>8671</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>OPT10_SCP</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz 100 [SCP]</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>2</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>OPT10_SCP</EXTERNAL_CODE>
        <EXTERNAL_CODE2>OPT10_SCP</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>null</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>6693</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>6693</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzzzzz (zzzz zzzz-zzz)  - zzzzz 0.07 + zzzzzzz (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>94;</EXTERNAL_CODE>
        <EXTERNAL_CODE2>94</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>434</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>386</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>386</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzz 0.07 (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>14</EXTERNAL_CODE>
        <EXTERNAL_CODE2>14</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525386</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>488</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>488</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>MTC Moczza - zzzzc zzacczz (zocezzzzzo c 1 cezzzzz)111</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>17</EXTERNAL_CODE>
        <EXTERNAL_CODE2>17</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>7000</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>7000</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzzz</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>7000</EXTERNAL_CODE>
        <EXTERNAL_CODE2>7000</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>7000</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>2</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>7002</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>7002</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzz zzzz</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>13;</EXTERNAL_CODE>
        <EXTERNAL_CODE2>13;</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
    <Row>
        <TARIFF_PLAN_ID>9900</TARIFF_PLAN_ID>
        <TARIFF_PLAN_CODE>9900</TARIFF_PLAN_CODE>
        <TARIFF_PLAN_NAME>zzz zzzzzz - zzzzzz zzz zzzzz zzzzzzz (zzzzzzzzzz z 61 zzzzzzz)</TARIFF_PLAN_NAME>
        <TARIFF_PLAN_NAME2>null</TARIFF_PLAN_NAME2>
        <BASIC_TARIFF_PLAN_ID>null</BASIC_TARIFF_PLAN_ID>
        <MAX_FRIENDLY_PHONES>0</MAX_FRIENDLY_PHONES>
        <DESCRIPTION>null</DESCRIPTION>
        <TARIFF_PLAN_TYPE>CU</TARIFF_PLAN_TYPE>
        <EXTERNAL_CODE>9900</EXTERNAL_CODE>
        <EXTERNAL_CODE2>9900</EXTERNAL_CODE2>
        <EXTERNAL_CODE3>525</EXTERNAL_CODE3>
        <SERVICE_PROVIDER_ID>1</SERVICE_PROVIDER_ID>
        <MAX_PARTIAL_BLOCK_DURATION>null</MAX_PARTIAL_BLOCK_DURATION>
    </Row>
</Table>
======================================="""),
("""2011-12-07 14:58:55,722 [10] DEBUG
=======================================
23085 - GetContracts - out parameter contract.StatusInfo=<IContractStatusInfo DateFrom="26.08.2008 14:43:27" DateTo="01.01.0001 0:00:00"><IContractStatus ID = "1" Code = "1" Name = "zzzzzz" /><ICrmUser ID = "-9223372036854775808" Name = "" /></IContractStatusInfo>
=======================================""",
"""2011-12-07 14:58:55,722 [10] DEBUG
=======================================
23085 - GetContracts - out parameter contract.StatusInfo=<IContractStatusInfo DateFrom="26.08.2008 14:43:27" DateTo="01.01.0001 0:00:00">
    <IContractStatus ID = "1" Code = "1" Name = "zzzzzz" />
    <ICrmUser ID = "-9223372036854775808" Name = "" />
</IContractStatusInfo>
=======================================""")
]


def diff(t1, t2):
 return "".join(difflib.ndiff(t1.splitlines(1), t2.splitlines(1)))

class TestPrettyXML(unittest.TestCase):
    def check(self, pxml_exp, pxml_real, n):
        self.assertEqual(pxml_exp, pxml_real,
            "%d parsed incorrectly:\n\n%s" % (n, diff(pxml_exp, pxml_real)))

if __name__ == '__main__':
    for n, xml in enumerate(xmls):
        pxml_real = prettify_xml(xml[0], sep="\n")
        def ch(xmle, xmlr, m):
            return lambda self: self.check(xmle, xmlr, m)
        setattr(TestPrettyXML, "test_%d" % n, ch(xml[1], pxml_real, n))
    unittest.main()
    #for xml in xmls:
    #    print prettify_xml(xml[0], sep="\n")
    #    print "\n\n"


import Cookies from "js-cookie";

export const getCountryName = (code) => {
    const countryMap = {
        AL: 'Albania',
        GR: 'Greece',
        BA: 'Bosnia and Herzegovina',
        ES: 'Spain',
        FR: 'France',
        IT: 'Italy',
        DE: 'Germany',
        AT: 'Austria',
        CH: 'Switzerland',
        PT: 'Portugal',
        HR: 'Croatia',
        RS: 'Serbia',
        MK: 'North Macedonia',
        MT: 'Malta',
        SI: 'Slovenia',
        ME: 'Montenegro',
        XK: 'Kosovo*',
        HU: 'Hungary',
        RO: 'Romania',
        BG: 'Bulgaria',
        PL: 'Poland',
        CZ: 'Czech Republic',
        SK: 'Slovakia',
        NL: 'Netherlands',
        BE: 'Belgium',
        LU: 'Luxembourg',
        DK: 'Denmark',
        SE: 'Sweden',
        NO: 'Norway',
        FI: 'Finland',
        IE: 'Ireland',
        GB: 'United Kingdom',
        IS: 'Iceland',
        LV: 'Latvia',
        EE: 'Estonia',
        LT: 'Lithuania',
        TR: 'Turkey',
        CY: 'Cyprus',
        UA: 'Ukraine',
        RU: 'Russia',
        AU: 'Australia',
        NZ: 'New Zealand',
        IL: 'Israel',
        CN: 'China',
        JP: 'Japan',
        KR: 'South Korea',
        IN: 'India',
        BR: 'Brazil',
        ZA: 'South Africa',
        EG: 'Egypt',
        MA: 'Morocco',
        TN: 'Tunisia',
        DZ: 'Algeria',
        AO: 'Angola',
        BJ: 'Benin',
        BW: 'Botswana',
        BF: 'Burkina Faso',
        BI: 'Burundi',
        CM: 'Cameroon',
        CV: 'Cape Verde',
        CF: 'Central African Republic',
        TD: 'Chad',
        KM: 'Comoros',
        CG: 'Congo (Brazzaville)',
        CD: 'Congo (Kinshasa)',
        CI: 'Côte d’Ivoire',
        DJ: 'Djibouti',
        GQ: 'Equatorial Guinea',
        ER: 'Eritrea',
        ET: 'Ethiopia',
        GA: 'Gabon',
        GM: 'Gambia',
        GH: 'Ghana',
        GN: 'Guinea',
        GW: 'Guinea-Bissau',
        KE: 'Kenya',
        LS: 'Lesotho',
        LR: 'Liberia',
        LY: 'Libya',
        MG: 'Madagascar',
        MW: 'Malawi',
        ML: 'Mali',
        MR: 'Mauritania',
        MU: 'Mauritius',
        MZ: 'Mozambique',
        NA: 'Namibia',
        NE: 'Niger',
        NG: 'Nigeria',
        RW: 'Rwanda',
        ST: 'São Tomé and Príncipe',
        SN: 'Senegal',
        SC: 'Seychelles',
        SL: 'Sierra Leone',
        SO: 'Somalia',
        SS: 'South Sudan',
        SD: 'Sudan',
        SZ: 'Eswatini',
        TZ: 'Tanzania',
        TG: 'Togo',
        UG: 'Uganda',
        ZM: 'Zambia',
        ZW: 'Zimbabwe',
        AF: 'Afghanistan',
        AM: 'Armenia',
        AZ: 'Azerbaijan',
        BH: 'Bahrain',
        BD: 'Bangladesh',
        BT: 'Bhutan',
        BN: 'Brunei',
        KH: 'Cambodia',
        GE: 'Georgia',
        ID: 'Indonesia',
        IR: 'Iran',
        IQ: 'Iraq',
        JO: 'Jordan',
        KZ: 'Kazakhstan',
        KW: 'Kuwait',
        KG: 'Kyrgyzstan',
        LA: 'Laos',
        LB: 'Lebanon',
        MY: 'Malaysia',
        MV: 'Maldives',
        MN: 'Mongolia',
        MM: 'Myanmar (Burma)',
        NP: 'Nepal',
        OM: 'Oman',
        PK: 'Pakistan',
        PH: 'Philippines',
        QA: 'Qatar',
        SA: 'Saudi Arabia',
        SG: 'Singapore',
        LK: 'Sri Lanka',
        SY: 'Syria',
        TJ: 'Tajikistan',
        TH: 'Thailand',
        TL: 'Timor-Leste',
        TM: 'Turkmenistan',
        AE: 'United Arab Emirates',
        UZ: 'Uzbekistan',
        VN: 'Vietnam',
        YE: 'Yemen',
        AG: 'Antigua and Barbuda',
        AW: 'Aruba',
        BS: 'Bahamas',
        BB: 'Barbados',
        BZ: 'Belize',
        PR: 'Puerto Rico',
        CA: 'Canada',
        CR: 'Costa Rica',
        CU: 'Cuba',
        DM: 'Dominica',
        DO: 'Dominican Republic',
        SV: 'El Salvador',
        GD: 'Grenada',
        GT: 'Guatemala',
        HT: 'Haiti',
        HN: 'Honduras',
        JM: 'Jamaica',
        MX: 'Mexico',
        NI: 'Nicaragua',
        PA: 'Panama',
        KN: 'Saint Kitts and Nevis',
        LC: 'Saint Lucia',
        VC: 'Saint Vincent and the Grenadines',
        VI: 'Virgin Islands (U.S.)',
        TT: 'Trinidad and Tobago',
        US: 'United States',
        AR: 'Argentina',
        BO: 'Bolivia',
        CL: 'Chile',
        CO: 'Colombia',
        EC: 'Ecuador',
        GY: 'Guyana',
        PY: 'Paraguay',
        PE: 'Peru',
        SR: 'Suriname',
        UY: 'Uruguay',
        VE: 'Venezuela',
        FK: 'Falkland Islands',
        AS: 'American Samoa',
        CK: 'Cook Islands',
        FJ: 'Fiji',
        PF: 'French Polynesia',
        GU: 'Guam',
        KI: 'Kiribati',
        MH: 'Marshall Islands',
        FM: 'Micronesia',
        NR: 'Nauru',
        NC: 'New Caledonia',
        NU: 'Niue',
        MP: 'Northern Mariana Islands',
        PW: 'Palau',
        PG: 'Papua New Guinea',
        WS: 'Samoa',
        CW: 'Curaçao',
        SB: 'Solomon Islands',
        SX: 'Sint Maarten',
        TK: 'Tokelau',
        TO: 'Tonga',
        TV: 'Tuvalu',
        VU: 'Vanuatu',
        WF: 'Wallis and Futuna',
        BM: 'Bermuda',
        GI: 'Gibraltar',
        AI: 'Anguilla',
        FO: 'Faroe Islands'
    };

    return countryMap[code.toUpperCase()] || code;
};

export const removeTextInBrackets = (str) => {
    return str.replace(/\s*\(.*?\)\s*/g, '').trim();
};

export const formatDateToNumbersAndLetters = (date) => {
    if (!date) return '';
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${year}-${month}-${day}`;
};

export const formatDateToMonthDayYear = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);

    const options = {year: 'numeric', month: 'short', day: 'numeric'};
    return d.toLocaleDateString('en-US', options);
};




export const loadLocationCookies = () => {
    let airportList = [];
    let selectedAirports = [];
    const startingPoint = Cookies.get("startingPoint") || "";

    try {
        const cookieAirportList = Cookies.get("airportList");
        if (cookieAirportList) {
            airportList = JSON.parse(cookieAirportList);
        }
    } catch (e) {
        console.error("Failed to parse airportList from cookies:", e);
    }

    try {
        const cookieSelectedAirports = Cookies.get("selectedAirports");
        if (cookieSelectedAirports) {
            selectedAirports = JSON.parse(cookieSelectedAirports);
        }
    } catch (e) {
        console.error("Failed to parse selectedAirports from cookies:", e);
    }

    return {startingPoint, airportList, selectedAirports};
};

export const getTagDescription = (tag) => {
    switch (tag) {
        case "summer_vacation":
            return "Summer Vacation";
        case "family_trip":
            return "Family Trip";
        case "mountains":
            return "Mountains";
        default:
            return tag;
    }
}
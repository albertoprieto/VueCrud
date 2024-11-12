import axios from 'axios';
import CryptoJS from 'crypto-js';
import { DateTime } from 'luxon';

// Constants
const OPENAPI_URL = "https://us-open.tracksolidpro.com/route/rest";
const APP_KEY = "8FB345B8693CCD006EB41604DD85DEBD";
const APP_SECRET = "b362f943f6a54ebfa9b27c489ddb75a4";
const ACCOUNT = "pgarcia1";
const PASSWORD_MD5 = "611b4f8ca88cb17e317f97b95c7c327a";

function getCurrentDate() {
    return DateTime.utc().toFormat('yyyy-MM-dd HH:mm:ss');
}

function generateSign(params, appSecret) {
    const sortedParams = Object.keys(params).sort().map(key => `${key}${params[key]}`).join('');
    const signStr = `${appSecret}${sortedParams}${appSecret}`;
    return CryptoJS.MD5(signStr).toString(CryptoJS.enc.Hex).toUpperCase();
}

async function sendPost(url, headers, data) {
    try {
        const response = await axios.post(url, new URLSearchParams(data), { headers });
        return response.data;
    } catch (error) {
        console.error('Error in sendPost:', error);
        throw error;
    }
}

function assemblyHeader(headers) {
    return { ...headers };
}

async function main() {
    const headerMap = {
        "Content-Type": "application/x-www-form-urlencoded"
    };

    const paramMap = {
        "app_key": APP_KEY,
        "v": "1.0",
        "timestamp": getCurrentDate(),
        "sign_method": "md5",
        "format": "json",
        "method": "jimi.oauth.token.get",
        "user_id": ACCOUNT,
        "user_pwd_md5": PASSWORD_MD5,
        "expires_in": "180"
    };

    try {
        const sign = generateSign(paramMap, APP_SECRET);
        paramMap["sign"] = sign;
    } catch (error) {
        console.error('Error generating sign:', error);
        return;
    }

    const response = await sendPost(OPENAPI_URL, assemblyHeader(headerMap), paramMap);

    if (response.code === 0) {
        const accessToken = response.result.accessToken;
        return await listSubAccounts(accessToken);
    } else {
        console.error('Error:', response.message);
        return [];
    }
}

async function listSubAccounts(accessToken) {
    const headerMap = {
        "Content-Type": "application/x-www-form-urlencoded"
    };

    const paramMap = {
        "app_key": APP_KEY,
        "v": "1.0",
        "timestamp": getCurrentDate(),
        "sign_method": "md5",
        "format": "json",
        "method": "jimi.user.child.list",
        "access_token": accessToken,
        "target": ACCOUNT
    };

    try {
        const sign = generateSign(paramMap, APP_SECRET);
        paramMap["sign"] = sign;
    } catch (error) {
        console.error('Error generating sign:', error);
        return [];
    }

    const response = await sendPost(OPENAPI_URL, assemblyHeader(headerMap), paramMap);

    if (response.code === 0) {
        const urls = [];
        for (const item of response.result) {
            if (item.account === 'Confitados' || item.account === 'confitados') {
                console.log(`Processing sub-account: ${item.account}`);
                const deviceUrls = await listDevices(accessToken, item.account);
                urls.push(...deviceUrls);
            }
        }
        return urls;
    } else {
        console.error('Error:', response.message);
        return [];
    }
}

async function listDevices(accessToken, targetAccount) {
    const headerMap = {
        "Content-Type": "application/x-www-form-urlencoded"
    };

    const paramMap = {
        "app_key": APP_KEY,
        "v": "1.0",
        "timestamp": getCurrentDate(),
        "sign_method": "md5",
        "format": "json",
        "method": "jimi.user.device.list",
        "access_token": accessToken,
        "target": targetAccount
    };

    try {
        const sign = generateSign(paramMap, APP_SECRET);
        paramMap["sign"] = sign;
    } catch (error) {
        console.error('Error generating sign:', error);
        return [];
    }

    const response = await sendPost(OPENAPI_URL, assemblyHeader(headerMap), paramMap);
    console.log(`Devices for sub-account ${targetAccount}:`, response);

    if (response.code === 0) {
        const urls = [];
        for (const device of response.result) {
            // if (device.imei === '862798052222789') {
                console.log('Procesando-----------');
                const url = await sendCommand(accessToken, device.imei);
                if (url) {
                    urls.push({ imei: device.imei, url });
                }
            // }
        }
        return urls;
    } else {
        console.error('Error:', response.message);
        return [];
    }
}

async function sendCommand(accessToken, imei) {
    const headerMap = {
        "Content-Type": "application/x-www-form-urlencoded"
    };

    const paramMap = {
        "app_key": APP_KEY,
        "v": "1.0",
        "timestamp": getCurrentDate(),
        "sign_method": "md5",
        "format": "json",
        "method": "jimi.open.video.rtmp.url",
        "access_token": accessToken,
        "imei": imei
    };

    try {
        const sign = generateSign(paramMap, APP_SECRET);
        paramMap["sign"] = sign;
    } catch (error) {
        console.error('Error generating sign:', error);
        return null;
    }

    const response = await sendPost(OPENAPI_URL, assemblyHeader(headerMap), paramMap);
    console.log(response.result);

    return response.result;
}

export default {
    main,
    listSubAccounts,
    listDevices,
    sendCommand
};
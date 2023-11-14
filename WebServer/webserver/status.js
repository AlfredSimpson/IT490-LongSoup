const statusMessageHandler = (req, res, next) => {
    res.statusMessageHandler = (statusCode) => {
        const statusMessages = {
            200: 'uhhh. OK',
            201: "Created! You're good to go.",
            202: 'ACK! We got your message.',
            204: 'No Content! Nothing to see here, I guess.',
            212: 'You are already logged in.',
            300: "Multiple Choices! We don't know what to do with you.",
            301: 'Moved Permanently! We moved, but you can still find us.',
            302: 'Found! We moved, but you can still find us - and did.',
            304: 'Not Modified! You already have the latest version.',
            305: 'Use Proxy! We are not allowed to talk to you directly.',
            307: 'Temporary Redirect! We moved, but you can still find us.',
            400: 'That is a Bad Request! You did something wrong.',
            401: 'Unauthorized! You are not allowed here.',
            402: 'Payment Required! You must pay to access this.',
            403: 'Forbidden! You are not allowed here.',
            404: 'Not Found! This does *not* rock.',
            405: 'Method Not Allowed! You cannot do that here.',
            406: 'Not Acceptable! We cannot give you what you want.',
            407: 'Proxy Authentication Required! You must authenticate.',
            408: 'Request Timeout! You took too long.',
            409: 'Conflict! You are not allowed to do that.',
            418: 'I am a teapot! I cannot do that.', // Legitimately a real error code
            500: 'Internal Server Error... you caught us slipping.',
            501: 'We would do anything for love... but we can\'t do that.',
            502: 'Bad Gateway! We cannot do that.',
            503: 'Come back later, we are sleeping.',
            // We can add more as needed
        };
        return statusMessages[statusCode] || 'Unknown Status';
    };
    next();
};

module.exports = statusMessageHandler;
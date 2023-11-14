const fs = require('fs'); // this engine requires the fs module

function alsviewer(filePath, options, callback) {
    console.log(`Passing through alsviewer.js, filePath: ${filePath}, options: ${options}, callback: ${callback}`);
    fs.readFile(filePath, function (err, content) {
        if (err) return callback(err);
        var rendered = content.toString();

        // Iterate through the keys in the options object and replace placeholders dynamically
        for (const key in options) {
            if (options.hasOwnProperty(key)) {
                const placeholder = `#${key}#`;
                const value = options[key];

                // Check if the value is not null or undefined before replacing the placeholder
                if (value !== null && value !== undefined) {
                    const stringValue = (typeof value === 'string') ? value : JSON.stringify(value);
                    const regex = new RegExp(placeholder, 'g'); // Use a global regex to replace all occurrences

                    // Replace all occurrences of the placeholder with the string value
                    rendered = rendered.replace(regex, stringValue);
                }
            }
        }

        return callback(null, rendered);
    });
}

module.exports = alsviewer;

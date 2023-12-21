// a function that creates a drop down that allows a user to select public or private

function getVisibility() {
    // create a dropdown that allows a user to select private or public
    var dropdown = document.createElement("select");
    dropdown.className = "form-select form-select-sm";
    dropdown.name = "privacy";
    dropdown.id = "privacy";
    dropdown.classList.add("mb-3");
    dropdown.classList.add("dropdown");
    dropdown.classList.add("btn-sm");

    var option1 = document.createElement("option");
    option1.value = "public";
    option1.innerText = "Public";

    var option2 = document.createElement("option");
    option2.value = "private";
    option2.innerText = "Private";

    dropdown.appendChild(option1);
    dropdown.appendChild(option2);
    return dropdown;

}

function createFileUpload() {
    var picUploadContainer = document.getElementById("picUpload");
    picUploadContainer.innerHTML = "";

    var frm = document.createElement("form");
    frm.id = "profilePictureUploadForm";
    frm.classList.add("mb-3");
    frm.method = "POST";
    frm.action = "/api/uploadProfilePic";
    frm.enctype = "multipart/form-data";
    picUploadContainer.appendChild(frm);

    // var pic_form = document.getElementById("profilePictureUploadForm");


    var label = document.createElement("label");
    label.htmlFor = "profilePictureUpload";
    label.className = "form-label";
    label.innerText = "Upload a picture";

    var input = document.createElement("input");
    input.className = "form-control form-control-sm";
    input.formEnctype = "multipart/form-data";
    input.id = "profilePictureUpload";
    input.type = "file";
    input.name = "profilePictureUpload";
    input.accept = "image/*";

    let vis = getVisibility();


    var sbmt = document.createElement("button");
    sbmt.type = "submit";
    sbmt.className = "btn btn-warning btn-sm";
    sbmt.innerText = "Save";
    sbmt.id = "profilePictureUploadBtn";

    frm.appendChild(label);
    frm.appendChild(input);
    frm.appendChild(vis);
    frm.appendChild(sbmt);

    picUploadContainer.appendChild(frm);
}

async function uploadPicture() {
    console.log(`uploading picture`);


    try {
        let form = document.getElementById("profilePictureUploadForm");
        let formData = new FormData(form);
        console.log(formData);

        const response = await axios.post('/api/uploadProfilePic', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data
    }
    catch (err) {
        console.log(err);
    }

}

function updateInformation(field_data) {
    let field_container = field_data + "-form";
    var fieldcontainer = document.getElementById(field_container);

    // var fieldcontainer = document.createElement("div");

    // var frm = document.createElement("form");
    // frm.id = field_data + "_upload";
    // frm.classList.add("mb-3");
    // frm.method = "POST";
    // frm.action = "/api/updateProfile";

    var label = document.createElement("label");
    label.htmlFor = `${field_data}_uploadform`;
    label.className = "form-label";
    label.innerText = "What's changed?";

    var input = document.createElement("input");
    input.className = "form-control form-control-sm";
    input.formEnctype = "text";
    input.id = `${field_data}_update`;
    input.type = "text";
    input.name = `${field_data}_uploadform`;
    input.accept = "text";

    let vis = getVisibility();


    var sbmt = document.createElement("button");
    sbmt.type = "submit";
    sbmt.className = "btn btn-warning btn-sm";
    sbmt.innerText = "Save";
    sbmt.id = `${field_data}_submit`;

    fieldcontainer.appendChild(label);
    fieldcontainer.appendChild(input);
    fieldcontainer.appendChild(vis);
    fieldcontainer.appendChild(sbmt);


    // fieldcontainer.appendChild(frm);

}


document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('username-btn').addEventListener('click', async (e) => {
        e.preventDefault();
        var usernameBtn = document.getElementById('username-btn');
        var usernameForm = document.getElementById('username-form');
        usernameForm.innerHTML = "";
        usernameBtn.style.display = "none";
        let f = "username";
        updateInformation(f);
        var submitBtn = document.getElementById("username_submit");
        submitBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            let username = document.getElementById("username_update").value;
            let privacy = document.getElementById("privacy").value;
            console.log(username);
            console.log(privacy);
            try {
                const response = await axios.post('/api/updateProfile', {
                    profile_field: "username",
                    field_data: username,
                    privacy: privacy
                });
                // if (response.data.error) {
                //     alert(response.data.error);
                // }
                // else {
                //     alert("Username updated!");
                // }
                console.log(response.data);
                usernameForm.innerHTML = "";
                usernameBtn.style.display = "block";
                try {
                    var userSbmt = document.getElementById("username_submit");
                    userSbmt.remove();
                    console.log("removed");
                }
                catch (err) {
                    console.log(err);
                }
                // var userSbmt = document.getElementById("username_submit");
                // userSbmt.remove();

            }
            catch (err) {
                console.log(err);
            }
        });
    });
    // document.getElementById("profilePic-btn").addEventListener("click", function (e) {
    //     e.preventDefault();
    //     createFileUpload();
    //     submitBtn = document.getElementById("profilePictureUploadBtn");
    //     submitBtn.addEventListener("click", function (e) {
    //         e.preventDefault();
    //         uploadPicture();
    //     });
    // });
});
document.addEventListener('DOMContentLoaded', function () {
    // Since there is so little js in this app, I'm leaving these in the global scope for now.

    const exerciseForm = document.getElementById('exercise-log-form');

    function getParams(form) {
        params = Object.values(form).reduce((obj, field) => {
            if (field.value !== '') {
                obj[field.name] = field.value;
            }

            return obj
        }, {});

        // Object will return an empty string property, we need to delete it.
        if (params.hasOwnProperty('')) {
            delete params[''];
        }

        return params
    }

    function createUrl(url, data) {
        let urlString = '';

        if (Object.keys(data).length === 0) {
            return url;
        } else {
            urlString = url + '?';
        }

        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                urlString += `${key}=${data[key]}&`
            }
        }

        return urlString;
    }

    if (exerciseForm) {
        exerciseForm.addEventListener('submit', function (e) {
            e.preventDefault();

            let formData = getParams(exerciseForm);
            window.location = createUrl('/api/exercise/log', formData);
        });
    }
});
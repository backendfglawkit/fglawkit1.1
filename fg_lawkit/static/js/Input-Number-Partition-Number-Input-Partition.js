window.addEventListener('load', function () {
    let elementsPartitionInput = document.getElementsByClassName('partition_input');
    for (let i = 0; i < elementsPartitionInput.length; i++) {

        elementsPartitionInput[i].addEventListener('keydown', function (event) {
            if (!isNumberByEvent(event) && !isTabClickByEvent(event) && !isBackspaceClickByEvent(event)) {
                event.preventDefault();
            }
        });

        elementsPartitionInput[i].addEventListener('keyup', function (event) {
            if (!isNumberByEvent(event) || isBackspaceClickByEvent(event)) {
                event.preventDefault();
            } else {

                let identifier = event.target.dataset.number_partition_identifier;
                let groupIdentifier = event.target.dataset.number_partition_group_identifier;

                if (identifier < getElementsGroup()[groupIdentifier].length - 1) {
                    identifier++;
                }

                getElementsGroup()[groupIdentifier][identifier].focus();
            }
        });

        elementsPartitionInput[i].addEventListener('focus', function (event) {
            let identifier = event.target.dataset.number_partition_identifier;
            let groupIdentifier = event.target.dataset.number_partition_group_identifier;

            getElementsGroup()[groupIdentifier][identifier].select();
        });
    }

    function getElementsGroup() {
        let elements = [];
        let lengthElementsOfList;
        let count = 0;
        while (lengthElementsOfList != 0) {
            let list = document.querySelectorAll('[data-number_partition_group_identifier="' + count + '"]');
            lengthElementsOfList = list.length;
            if (lengthElementsOfList != 0)
                elements.push(list);
            count++;
        }
        return elements;
    }

    function isNumberByEvent(event) {
        let response = false;
        for (let number = 0; number <= 9; number++) {
            if (event.key == number && event.key != " ") {
                response = true;
                break;
            }
        }
        return response;
    }

    function isTabClickByEvent(event) {
        let response = false;

        if (event.key == 'Tab') {
            response = true;
        }
        return response;
    }

    function isBackspaceClickByEvent(event) {
        let response = false;

        if (event.key == 'Backspace') {
            response = true;
        }
        return response;
    }
});
.. raw:: html

    <script type="text/javascript">
        function update_tabs() {
            let anchor_point = window.location.hash;
            let tabs = document.querySelectorAll(".tab-content");

            function activate_iffound(element, text, attr) {
                element.classList.remove("selected");
                if (element.getAttribute(attr).indexOf(text) > -1) {
                    element.className += " selected";
                }
            }

            // select a yaml tab
            if (anchor_point.indexOf("yaml") > -1) {
                for (let i = 0; i < tabs.length; i++) {
                    activate_iffound(tabs[i], "yaml", "id");
                }
                // select a toml tab
            } else if (anchor_point.indexOf("toml") > -1) {
                for (let i = 0; i < tabs.length; i++) {
                    activate_iffound(tabs[i], "toml", "id");
                }
                // select a jsonml tab or by default
            } else {
                for (let i = 0; i < tabs.length; i++) {
                    activate_iffound(tabs[i], "json", "id");
                }
            }
        }

        window.addEventListener("hashchange", update_tabs, false);
        document.addEventListener("readystatechange", function () {
            if (document.readyState === "complete") update_tabs();
        }, false);
    </script>
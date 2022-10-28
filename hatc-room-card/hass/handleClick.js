export default (node, hass, config, entityId) => {
    let e;
    if (!config){
        console.log("not config!");
        return;
    }

    console.log("handleClick: switch->");
    // eslint-disable-next-line default-case
    switch (config.action) {
        case 'more-info': {
            console.log("handleClick: more-info");
            e = new Event('hass-more-info', { composed: true });
            e.detail = {
            entityId: config.entity || entityId,
            };
            node.dispatchEvent(e);
            break;
        }
        case 'navigate': {
            console.log("handleClick: navigate");
            if (!config.navigation_path) return;
            window.history.pushState(null, '', config.navigation_path);
            e = new Event('location-changed', { composed: true });
            e.detail = { replace: false };
            window.dispatchEvent(e);
            break;
        }
        case 'call-service': {
            console.log("handleClick: call-service");
            if (!config.service) return;
            const [domain, service] = config.service.split('.', 2);
            const serviceData = { ...config.service_data };
            hass.callService(domain, service, serviceData);
            break;
        }
        case 'url': {
            console.log("handleClick: url");
            if (!config.url) return;
            window.location.href = config.url;
        }
    }
};
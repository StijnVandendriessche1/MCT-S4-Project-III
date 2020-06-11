const fetchData = async function (url, method = "GET", body = null) {
  return fetch(`${ip}/api/v1/${url}`, {
    method: method,
    body: body,
    headers: { "content-type": "application/json" },
  })
    .then((r) => r.json())
    .then((data) => data);
};
let getAPI = async function (url, callback, method = "GET", body = null) {
  try {
    const data = await fetchData(url, method, body);
    callback(data);
  } catch (error) {
  }
};

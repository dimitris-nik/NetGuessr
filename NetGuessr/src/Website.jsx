
export default function Website({url}) {
    const filtered_url = "http://localhost:5000/filter?url=" + url;
    return (
    <div className="iframe-container">
        {url.length > 0 && <iframe src={filtered_url} title="Website" />}
        {/* {url.length === 0 && <div className="loader"></div>} */}
    </div>)
}
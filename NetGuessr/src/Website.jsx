import  { useEffect, useState } from 'react'
import { Dot } from "react-animated-dots";

export default function Website({url}) {
    return (
    <div className="iframe-container">
        {url.length > 0 && <iframe src={url} title="Website" />}
        {url.length === 0 && <p>Loading<Dot>.</Dot><Dot>.</Dot><Dot>.</Dot></p>}
    </div>)
}
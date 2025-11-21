import React from 'react'

function FilterBlock({ label, children }) {
    return (
        <div>
            <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>{label}</div>
            {children}
        </div>
    )
}

export default FilterBlock

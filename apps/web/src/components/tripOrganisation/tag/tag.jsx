import React, {forwardRef} from "react";
import './styles.css';
import '../../../commonStyles.css';

const Tag = forwardRef(({id, icon, alt, onClick, isSelected}, ref) => {
    const handleClick = () => {
        // Directly use onClick with id
        onClick(id);
    };

    return (
        <div className={`text-wrapper ${isSelected ? 'selected' : ''}`} onClick={handleClick}>
            <div className={`tag ${isSelected ? 'selected' : ''}`}>
                <img ref={ref} src={icon} alt={alt} className={`tag-icon ${isSelected ? '' : ''}`}/>
            </div>
            <div className={"text-tag"}>{alt}</div> {/* Fixed conditional rendering */}
        </div>
    );
});

export default Tag;
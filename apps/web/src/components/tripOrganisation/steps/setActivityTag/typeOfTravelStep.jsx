import React, {forwardRef, useState} from "react";
import SkiingIcon from "../../../../images/tags/travel_type/v3/ski-svgrepo-com.svg";
import SummerVacationIcon from "../../../../images/tags/travel_type/v3/summer-svgrepo-com.svg";
import HikingIcon from "../../../../images/tags/travel_type/v3/hiking-svgrepo-com-2.svg";
import FamilyTripIcon from "../../../../images/tags/travel_type/v3/family-svgrepo-com.svg";
import LakesIcon from "../../../../images/tags/travel_type/v3/lake-svgrepo-com.svg";
import ParachuteIcon from "../../../../images/tags/travel_type/v3/parachute-svgrepo-com.svg";
import CavingIcon from "../../../../images/tags/travel_type/v3/underground-cave-svgrepo-com.svg";
import MountainIcon from "../../../../images/destinations/tags/mountain-svgrepo-com.svg";

import Tag from "../../tag/tag.jsx";
import CustomNextButton from "../../buttons/customNextButton.jsx";

const TagSelection = forwardRef(({tagsExpanded, onTagSelect, onSearchClick}, ref) => {
    const [selectedTagId, setSelectedTagId] = useState(null); // Store the ID of the selected tag

    const handleTagClick = (tagId) => {
        if (selectedTagId === tagId) { // Check if the clicked tag is already selected
            setSelectedTagId(null);       // If so, deselect it
            onTagSelect(null);           // and notify parent
        } else {
            setSelectedTagId(tagId);     // Otherwise, select the clicked tag
            onTagSelect(tagId);       // and notify parent
        }
    };

    const tags = [
        {id: "skiing", icon: SkiingIcon, alt: "Skiing"},
        {id: "summer_vacation", icon: SummerVacationIcon, alt: "Summer Vacation"},
        {id: "hiking", icon: HikingIcon, alt: "Hiking"},
        {id: "mountains", icon: MountainIcon, alt: "Mountains"},
        {id: "family_trip", icon: FamilyTripIcon, alt: "Family Trip"},
        {id: "lakes", icon: LakesIcon, alt: "Lakes"},
        {id: "parachuting", icon: ParachuteIcon, alt: "Parachuting"},
        {id: "caving", icon: CavingIcon, alt: "Caving"},
    ];

    if (tagsExpanded) {
        return (
            <div id={"tag-container"} className={"tag-wrapper bottom-shadow rounded-button"}>
                <p className={"input-box-title"}>What you want to do?</p>
                <div className="tags-container expanded">
                    {tags.map((tag) => (
                        <Tag
                            key={tag.id}
                            id={tag.id}
                            icon={tag.icon}
                            alt={tag.alt}
                            onClick={handleTagClick}
                            isSelected={tag.id === selectedTagId}
                            ref={ref}
                        />
                    ))}
                </div>
                <div className={"empty-space"}></div>
                <div className={"input-navigation"}>
                    <CustomNextButton text={"Search"} onClick={onSearchClick} color={"nav-color"}/>
                </div>
            </div>
        );
    } else {
        return (
            <div className={"tags-container collapsed bottom-shadow rounded-button"}>
                <div className="disabled-text rounded-left-button">What</div>
                <div className={`activity-tag ${selectedTagId ? "" : "unselected"}`}>{!selectedTagId && (
                    <div>Type of activity</div>)}
                    {selectedTagId && (
                        <div>{selectedTagId}</div>)}</div>
            </div>
        );
    }

});

export default TagSelection;

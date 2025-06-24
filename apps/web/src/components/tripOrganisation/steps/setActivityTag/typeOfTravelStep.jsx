import React, {forwardRef} from "react";
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
import {useDispatch, useSelector} from "react-redux";
import {setTag} from "@picotrip/shared/src/store/actions/tripOrganisationActions.jsx";



const TagSelection = forwardRef(({tagsExpanded, onSearchClick}, ref) => {

    const dispatch = useDispatch();

    const selectedTag = useSelector((state) => state.tripOrganisation.tag);
    const handleTagClick = (tagId) => {
        if (selectedTag === tagId) { // Check if the clicked tag is already selected
            dispatch(setTag(null))
        } else {
            dispatch(setTag(tagId))
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
                            isSelected={tag.id === selectedTag}
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
                <div className={`activity-tag ${selectedTag ? "" : "unselected"}`}>{!selectedTag && (
                    <div>Type of activity</div>)}
                    {selectedTag && (
                        <div>{selectedTag}</div>)}</div>
            </div>
        );
    }

});

export default TagSelection;

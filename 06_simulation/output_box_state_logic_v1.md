# Output Box State Logic v1

## States

- available: target category can receive tubes.
- near_full: target category can still receive tubes but should warn the operator.
- full: no new normal tubes of this category may be placed.
- service_required: operator must clear or replace the output box.
- replaced: operator has installed an empty or available box and the category can resume.

## Full Category Rule

If one category output box is full:

- Pause tasks for that category.
- Do not send normal tubes of that category to manual review.
- Continue processing other categories with available output boxes.
- Resume the paused category after manual clearing or box replacement.

Manual review is only for abnormal tubes, not capacity management.

